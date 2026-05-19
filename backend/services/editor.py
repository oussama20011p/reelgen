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
        vids_looped = (vids * ((10 // len(vids)) + 1))[:10] if len(vids) < 10 else vids[:10]
        clip_dur = round(DURATION / len(vids_looped), 2)

        clips = []
        for i, vid in enumerate(vids_looped):
            out = f"{tmp}/clip_{i:02d}.mp4"
            start = random.uniform(0.5, 2)
            r = subprocess.run([
                FFMPEG, "-y", "-ss", str(start), "-i", vid, "-t", str(clip_dur),
                "-vf", (
                    f"scale={REEL_W*2}:{REEL_H*2}:force_original_aspect_ratio=increase,"
                    f"crop={REEL_W*2}:{REEL_H*2},"
                    f"scale={REEL_W}:{REEL_H}:flags=lanczos,setsar=1"
                ),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an", "-r", "30", out
            ], capture_output=True)
            if os.path.exists(out) and os.path.getsize(out) > 1000:
                clips.append(out)

        if not clips:
            raise ValueError("No clips processed")

        concat_file = f"{tmp}/concat.txt"
        with open(concat_file, "w") as f:
            for c in clips:
                f.write(f"file '{c}'\n")

        merged = f"{tmp}/merged.mp4"
        subprocess.run(
            [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", merged],
            capture_output=True, check=True
        )

        audio_filter = f"[1:a]volume=2.0,adelay=1000|1000,afade=t=out:st={DURATION-2}:d=2[aout]"
        subprocess.run([
            FFMPEG, "-y",
            "-i", merged, "-i", voiceover_path,
            "-t", str(DURATION),
            "-map", "0:v:0",
            "-filter_complex", audio_filter,
            "-map", "[aout]",
            "-vf", f"fade=t=in:st=0:d=0.3,fade=t=out:st={DURATION-1}:d=1",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
        ], check=True, capture_output=True)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return output_path
