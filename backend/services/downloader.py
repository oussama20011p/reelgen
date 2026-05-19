import os
import httpx

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "tiktok-video-no-watermark2.p.rapidapi.com"


def search_tiktok_urls(keywords: str) -> list:
    """Search TikTok for videos related to keywords via RapidAPI."""
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    urls = []
    try:
        r = httpx.get(
            "https://tiktok-video-no-watermark2.p.rapidapi.com/feed/search",
            params={"keywords": keywords, "count": "20", "cursor": "0", "region": "MA", "publish_time": "0"},
            headers=headers,
            timeout=15,
        )
        data = r.json()
        items = data.get("data", {}).get("videos", []) or []
        for item in items:
            url = item.get("play") or item.get("wmplay") or ""
            if url:
                urls.append(("tiktok", url, item.get("title", "video")[:40]))
    except Exception:
        pass
    return urls


def download_video_from_url(url: str, output_path: str) -> bool:
    """Download a direct mp4 URL to output_path."""
    try:
        with httpx.stream("GET", url, timeout=30, follow_redirects=True) as r:
            if r.status_code != 200:
                return False
            with open(output_path, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        return os.path.getsize(output_path) > 10000
    except Exception:
        return False


def download_videos(urls: list, output_dir: str, keywords: str = "") -> list:
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []

    # Search TikTok via RapidAPI
    video_items = search_tiktok_urls(keywords or " ".join(urls[:3]) if urls else "product review")

    for i, (source, video_url, title) in enumerate(video_items[:20]):
        if len(downloaded) >= 15:
            break
        safe_title = "".join(c for c in title if c.isalnum() or c in " _-")[:30]
        out_path = os.path.join(output_dir, f"{i:02d}_{safe_title}.mp4")
        if download_video_from_url(video_url, out_path):
            downloaded.append(out_path)

    # fallback: collect existing mp4s
    if not downloaded:
        downloaded = [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.endswith(".mp4")
        ]

    return downloaded
