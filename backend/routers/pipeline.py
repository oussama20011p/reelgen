from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import asyncio
import os
import uuid
import time
from services import analyze, scripts, voiceover, downloader, editor

router = APIRouter()

# Store active jobs: job_id -> {"status", "steps", "result", "error", "last_seen"}
jobs: dict = {}

TEMP_BASE = "/tmp/reelgen"
os.makedirs(TEMP_BASE, exist_ok=True)


@router.post("/start")
async def start_pipeline(
    image: UploadFile = File(...),
    language: str = Form(...),
    invite_code: str = Form(...),
    manual_script: str = Form(""),
):
    valid_codes = os.getenv("INVITE_CODES", "oussama2025,sadaka,reelgen").split(",")
    valid_codes = [c.strip() for c in valid_codes if c.strip()]
    if invite_code not in valid_codes:
        raise HTTPException(status_code=401, detail="Code invalide")

    job_id = str(uuid.uuid4())
    image_bytes = await image.read()
    mime_type = image.content_type or "image/jpeg"

    jobs[job_id] = {
        "status": "queued",
        "steps": [],
        "result": None,
        "error": None,
        "last_seen": time.time()
    }

    asyncio.create_task(run_pipeline(job_id, image_bytes, mime_type, language, manual_script))
    return {"job_id": job_id}


@router.get("/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    job["last_seen"] = time.time()
    return {
        "status": job["status"],
        "steps": job["steps"],
        "result": job["result"],
        "error": job["error"],
    }


@router.get("/download/{job_id}/{version}")
def download_reel(job_id: str, version: str):
    job_dir = os.path.join(TEMP_BASE, job_id)
    path = os.path.join(job_dir, f"reel_v{version}.mp4")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="video/mp4", filename=f"reel_{version}.mp4")


def push(job_id: str, message: str):
    if job_id in jobs:
        jobs[job_id]["steps"].append(message)


async def run_pipeline(job_id: str, image_bytes: bytes, mime_type: str, language: str, manual_script: str = ""):
    job_dir = os.path.join(TEMP_BASE, job_id)
    video_dir = os.path.join(job_dir, "videos")
    os.makedirs(video_dir, exist_ok=True)

    # Save product image to disk
    product_image_path = os.path.join(job_dir, "product_image.jpg")
    with open(product_image_path, "wb") as f:
        f.write(image_bytes)

    try:
        jobs[job_id]["status"] = "running"

        # Step 1 — Analyze image
        push(job_id, "🔍 Analyse du produit...")
        product = await asyncio.to_thread(analyze.analyze_product_image, image_bytes, mime_type)
        push(job_id, f"✅ Produit: {product['name']}")

        # Step 2 — Generate scripts
        if manual_script.strip():
            push(job_id, "✍️ Script manuel utilisé...")
            s = {"hook": manual_script.strip(), "body": "", "cta": "", "angle": "Manuel"}
            scripts_data = {"A": s, "B": s, "C": s}
            push(job_id, "✅ Script manuel appliqué aux 3 reels")
        else:
            push(job_id, "✍️ Génération des scripts...")
            scripts_data = await asyncio.to_thread(scripts.generate_scripts, product, language)
            push(job_id, "✅ 3 scripts générés (A/B/C)")

        # Step 3 — Download videos
        push(job_id, "🎬 Recherche vidéos via RapidAPI...")
        keywords = product.get("tiktok_search") or product.get("niche") or product["name"]
        downloaded = await asyncio.to_thread(downloader.download_videos, [], video_dir, keywords)
        push(job_id, f"✅ {len(downloaded)} vidéos téléchargées")

        # Step 4 — Voice overs
        push(job_id, "🎙️ Génération voice overs...")
        vo_paths = {}
        for v in ["A", "B", "C"]:
            script = scripts_data[v]
            text = f"{script['hook']} {script['body']} {script['cta']}"
            vo_path = os.path.join(job_dir, f"voiceover_{v}.wav")
            await asyncio.to_thread(voiceover.generate_voiceover, text, vo_path)
            vo_paths[v] = vo_path
            push(job_id, f"✅ Voice over {v} OK")

        # Step 5 — Edit reels
        push(job_id, "🎞️ Montage des reels...")
        for v in ["A", "B", "C"]:
            out = os.path.join(job_dir, f"reel_v{v}.mp4")
            await asyncio.to_thread(editor.make_reel, video_dir, vo_paths[v], out, product_image_path)
            size_mb = round(os.path.getsize(out) / (1024 * 1024), 1)
            push(job_id, f"✅ Reel {v} — {size_mb} MB")

        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = {
            "product": product,
            "scripts": scripts_data,
            "reels": {v: f"/api/download/{job_id}/{v}" for v in ["A", "B", "C"]}
        }

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        push(job_id, f"❌ Erreur: {str(e)}")
