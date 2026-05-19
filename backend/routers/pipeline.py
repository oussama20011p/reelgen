from fastapi import APIRouter, UploadFile, File, Form, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
import asyncio
import json
import os
import uuid
import shutil
from services import analyze, scripts, voiceover, downloader, editor

router = APIRouter()

# Store active jobs: job_id -> {"status", "progress", "result", "error"}
jobs: dict = {}

TEMP_BASE = "/tmp/reelgen"
os.makedirs(TEMP_BASE, exist_ok=True)


@router.post("/start")
async def start_pipeline(
    image: UploadFile = File(...),
    language: str = Form(...),
    invite_code: str = Form(...),
):
    # Verify invite code
    valid_codes = os.getenv("INVITE_CODES", "").split(",")
    valid_codes = [c.strip() for c in valid_codes if c.strip()]
    if invite_code not in valid_codes:
        raise HTTPException(status_code=401, detail="Code invalide")

    job_id = str(uuid.uuid4())
    image_bytes = await image.read()
    mime_type = image.content_type or "image/jpeg"

    jobs[job_id] = {"status": "queued", "progress": [], "result": None, "error": None}

    # Run pipeline in background
    asyncio.create_task(run_pipeline(job_id, image_bytes, mime_type, language))

    return {"job_id": job_id}


@router.websocket("/ws/{job_id}")
async def pipeline_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()
    try:
        while True:
            if job_id not in jobs:
                await websocket.send_json({"type": "error", "message": "Job not found"})
                break

            job = jobs[job_id]
            # Send all pending progress messages
            while job["progress"]:
                msg = job["progress"].pop(0)
                await websocket.send_json(msg)

            if job["status"] == "done":
                await websocket.send_json({"type": "done", "result": job["result"]})
                break
            elif job["status"] == "error":
                await websocket.send_json({"type": "error", "message": job["error"]})
                break

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass


@router.get("/download/{job_id}/{version}")
def download_reel(job_id: str, version: str):
    job_dir = os.path.join(TEMP_BASE, job_id)
    path = os.path.join(job_dir, f"reel_v{version}.mp4")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="video/mp4", filename=f"reel_{version}.mp4")


def push(job_id: str, msg: dict):
    if job_id in jobs:
        jobs[job_id]["progress"].append(msg)


async def run_pipeline(job_id: str, image_bytes: bytes, mime_type: str, language: str):
    job_dir = os.path.join(TEMP_BASE, job_id)
    video_dir = os.path.join(job_dir, "videos")
    os.makedirs(video_dir, exist_ok=True)

    try:
        jobs[job_id]["status"] = "running"

        # Step 1 — Analyze image
        push(job_id, {"type": "step", "step": 1, "message": "🔍 Analyse du produit..."})
        product = await asyncio.to_thread(analyze.analyze_product_image, image_bytes, mime_type)
        push(job_id, {"type": "product", "data": product})
        push(job_id, {"type": "step", "step": 1, "message": f"✅ Produit: {product['name']}"})

        # Step 2 — Generate scripts
        push(job_id, {"type": "step", "step": 2, "message": "✍️ Génération des scripts..."})
        scripts_data = await asyncio.to_thread(scripts.generate_scripts, product, language)
        push(job_id, {"type": "scripts", "data": scripts_data})
        push(job_id, {"type": "step", "step": 2, "message": "✅ 3 scripts générés (A/B/C)"})

        # Step 3 — Search & download videos
        push(job_id, {"type": "step", "step": 3, "message": "🎬 Recherche et téléchargement vidéos..."})
        keywords = " ".join(product.get("keywords", [product["name"]])[:3])
        urls = build_search_urls(keywords)
        downloaded = await asyncio.to_thread(downloader.download_videos, urls, video_dir)
        push(job_id, {"type": "step", "step": 3, "message": f"✅ {len(downloaded)} vidéos téléchargées"})

        # Step 4 — Voice overs
        push(job_id, {"type": "step", "step": 4, "message": "🎙️ Génération voice overs..."})
        vo_paths = {}
        for v in ["A", "B", "C"]:
            script = scripts_data[v]
            text = f"{script['hook']} {script['body']} {script['cta']}"
            vo_path = os.path.join(job_dir, f"voiceover_{v}.wav")
            await asyncio.to_thread(voiceover.generate_voiceover, text, vo_path)
            vo_paths[v] = vo_path
            push(job_id, {"type": "step", "step": 4, "message": f"✅ Voice over {v} OK"})

        # Step 5 — Edit reels
        push(job_id, {"type": "step", "step": 5, "message": "🎞️ Montage des reels..."})
        reel_paths = {}
        for v in ["A", "B", "C"]:
            out = os.path.join(job_dir, f"reel_v{v}.mp4")
            await asyncio.to_thread(editor.make_reel, video_dir, vo_paths[v], out)
            size_mb = round(os.path.getsize(out) / (1024 * 1024), 1)
            reel_paths[v] = out
            push(job_id, {"type": "step", "step": 5, "message": f"✅ Reel {v} — {size_mb} MB"})

        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = {
            "product": product,
            "scripts": scripts_data,
            "reels": {v: f"/api/download/{job_id}/{v}" for v in ["A", "B", "C"]}
        }

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        push(job_id, {"type": "error", "message": f"❌ Erreur: {str(e)}"})


def build_search_urls(keywords: str) -> list:
    # Return a curated list of known working TikTok URLs + search-based ones
    # In production these come from a real search; here we seed with known patterns
    return [
        f"https://www.tiktok.com/search/video?q={keywords.replace(' ', '%20')}",
    ]
