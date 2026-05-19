import yt_dlp
import os

def download_videos(urls: list, output_dir: str) -> list:
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        "outtmpl": output_dir + "/%(title).40s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
    }
    downloaded = []
    for url in urls:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                w = info.get("width", 0)
                h = info.get("height", 0)
                if w and h and w > h:
                    continue  # skip 16:9
                title = info.get("title", "video")[:40]
                path = os.path.join(output_dir, f"{title}.mp4")
                if os.path.exists(path):
                    downloaded.append(path)
        except Exception:
            continue
    # fallback: collect all mp4s in dir
    if not downloaded:
        downloaded = [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.endswith(".mp4")
        ]
    return downloaded
