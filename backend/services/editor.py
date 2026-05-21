import subprocess
import glob
import random
import os
import shutil
import tempfile

FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg")
REEL_W, REEL_H = 1080, 1920
DURATION = 30


def make_reel(video_dir: str, voiceover_path: str, output_path: str) -> str:
    all_vids = glob.glob(f"{video_dir}/*.mp4")
    if not all_vids:
        raise ValueError("No videos found in directory")

    tmp = tempfile.mkdtemp()
    try:
        vids = all_vids.copy()
        random.shuffle(vids)
        nb_clips = 5
        vids_looped = (vids * ((nb_clips // len(vids)) + 1))[:nb_clips] if len(vids) < nb_clips else vids[:nb_clips]
        clip_dur = round(DURATION / nb_clips, 2)

        vf = f"scale={REEL_W}:{REEL_H}:force_original_aspect_ratio=decrease,pad={REEL_W}:{REEL_H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
        clips = []
        errors = []
        for i, vid in enumerate(vids_looped):
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
            [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", merged],
            capture_output=True, check=True
        )

        subprocess.run([
            FFMPEG, "-y",
            "-i", merged, "-i", voiceover_path,
            "-t", str(DURATION),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest", output_path
        ], check=True, capture_output=True)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return output_path
