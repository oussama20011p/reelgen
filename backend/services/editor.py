import subprocess
import glob
import random
import os
import shutil
import tempfile

FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg")
REEL_W, REEL_H = 1080, 1920
DURATION = 30
NB_CLIPS = 5


def _image_clip(image_path: str, out: str, movement: int, clip_dur: float) -> bool:
    frames = int(clip_dur * 30)
    movements = [
        f"zoompan=z='min(zoom+0.0015,1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}",
        f"zoompan=z='if(lte(on,1),1.4,max(zoom-0.0015,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}",
        f"zoompan=z='1.2':x='if(lte(on,1),0,min(x+3,iw*0.2))':y='ih/2-(ih/zoom/2)':d={frames}",
        f"zoompan=z='1.2':x='if(lte(on,1),iw*0.2,max(x-3,0))':y='ih/2-(ih/zoom/2)':d={frames}",
        f"zoompan=z='min(zoom+0.001,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}",
    ]
    mv = movements[movement % len(movements)]
    vf = (
        f"scale={REEL_W}:{REEL_H}:force_original_aspect_ratio=decrease,"
        f"pad={REEL_W}:{REEL_H}:(ow-iw)/2:(oh-ih)/2:black,"
        f"{mv},setsar=1"
    )
    r = subprocess.run([
        FFMPEG, "-y", "-loglevel", "error",
        "-loop", "1", "-i", image_path,
        "-t", str(clip_dur), "-vf", vf,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-threads", "1", "-r", "30", "-pix_fmt", "yuv420p", "-an", out
    ], capture_output=True)
    return os.path.exists(out) and os.path.getsize(out) > 500


def make_reel(video_dir: str, voiceover_path: str, output_path: str, product_image: str = None) -> str:
    tmp = tempfile.mkdtemp()
    try:
        clip_dur = round(DURATION / NB_CLIPS, 2)
        clips = []

        # Use product image with animations
        if product_image and os.path.exists(product_image):
            for i in range(NB_CLIPS):
                out = f"{tmp}/clip_{i:02d}.mp4"
                if _image_clip(product_image, out, i, clip_dur):
                    clips.append(out)

        # Fallback to TikTok videos if image clips failed
        if not clips:
            all_vids = glob.glob(f"{video_dir}/*.mp4")
            if not all_vids:
                raise ValueError("No videos found in directory")
            vids = all_vids.copy()
            random.shuffle(vids)
            vids_sel = (vids * ((NB_CLIPS // len(vids)) + 1))[:NB_CLIPS] if len(vids) < NB_CLIPS else vids[:NB_CLIPS]
            vf = (
                f"scale={REEL_W}:{REEL_H}:force_original_aspect_ratio=decrease,"
                f"pad={REEL_W}:{REEL_H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
            )
            errors = []
            for i, vid in enumerate(vids_sel):
                out = f"{tmp}/clip_{i:02d}.mp4"
                succeeded = False
                for start in [0, random.uniform(0.5, 2.0)]:
                    r = subprocess.run([
                        FFMPEG, "-y", "-loglevel", "error",
                        "-ss", str(start), "-i", vid,
                        "-t", str(clip_dur), "-vf", vf,
                        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
                        "-threads", "1", "-an", "-r", "30", "-pix_fmt", "yuv420p", out
                    ], capture_output=True)
                    if os.path.exists(out) and os.path.getsize(out) > 500:
                        clips.append(out)
                        succeeded = True
                        break
                    if os.path.exists(out):
                        os.remove(out)
                if not succeeded:
                    errors.append(r.stderr.decode(errors="replace")[-200:] if r else "unknown")
            if not clips:
                detail = errors[0] if errors else "no output"
                raise ValueError(f"No clips processed. FFmpeg: {detail}")

        concat_file = f"{tmp}/concat.txt"
        with open(concat_file, "w") as f:
            for c in clips:
                f.write(f"file '{c}'\n")

        merged = f"{tmp}/merged.mp4"
        subprocess.run(
            [FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", concat_file, "-c", "copy", merged],
            capture_output=True, check=True
        )

        subprocess.run([
            FFMPEG, "-y", "-loglevel", "error",
            "-i", merged, "-i", voiceover_path,
            "-t", str(DURATION),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest", output_path
        ], check=True, capture_output=True)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return output_path
