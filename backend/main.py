from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import pipeline, auth
import uvicorn

app = FastAPI(title="ReelGen API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")

@app.get("/health")
def health():
    import subprocess, glob
    ffmpeg_ok = subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode == 0
    videos = glob.glob("/tmp/reelgen/**/*.mp4", recursive=True)[:3]
    probe = {}
    for v in videos:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "stream=codec_name,width,height,duration", "-of", "json", v],
            capture_output=True, text=True)
        probe[v.split("/")[-1]] = r.stdout[:300] or r.stderr[:200]
    return {"status": "ok", "version": "v3", "ffmpeg": ffmpeg_ok, "probe": probe}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
