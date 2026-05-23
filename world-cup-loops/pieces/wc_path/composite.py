"""Composite a cinematic AI-generated opener with our data-driven path explainer.

Layout:
  [0 - N seconds]    cinematic opener (AI generated, e.g. Veo / Hailuo / Seedance)
  [crossfade 0.3s]
  [N+0.3s - end]     path explainer (our deterministic data viz)

Usage:
  python composite.py <country_code> <opener_mp4_path>
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "output"


def probe_duration(path: Path) -> float:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    ffprobe = ffmpeg.replace("ffmpeg", "ffprobe")
    if not Path(ffprobe).exists():
        # Fall back: ask ffmpeg via stderr
        result = subprocess.run(
            [ffmpeg, "-i", str(path)],
            capture_output=True, text=True
        )
        for line in result.stderr.split("\n"):
            if "Duration:" in line:
                t = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = t.split(":")
                return float(h) * 3600 + float(m) * 60 + float(s)
        return 0.0
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def composite(country_code: str, opener_path: Path):
    country_code = country_code.upper()
    path_mp4 = OUT_DIR / f"wc_path_{country_code}.mp4"
    if not path_mp4.exists():
        sys.exit(f"!! data piece missing: {path_mp4}. run render.py {country_code} first.")
    if not opener_path.exists():
        sys.exit(f"!! opener missing: {opener_path}")

    opener_dur = probe_duration(opener_path)
    path_dur = probe_duration(path_mp4)
    print(f"opener: {opener_dur:.2f}s, path explainer: {path_dur:.2f}s")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out = OUT_DIR / f"wc_hybrid_{country_code}.mp4"

    # Normalize both clips to same fps/resolution first (1080x1920 @ 30fps).
    # The opener may be 1080p / 9:16 at varying fps; force scale + fps.
    norm_opener = HERE / f"_norm_opener_{country_code}.mp4"
    norm_path = HERE / f"_norm_path_{country_code}.mp4"

    print(">>> normalizing opener")
    subprocess.run([
        ffmpeg, "-y", "-i", str(opener_path),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-an", str(norm_opener),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(">>> normalizing path explainer")
    # Path piece is already 1080x1920/30 but re-encode for clean concat
    subprocess.run([
        ffmpeg, "-y", "-i", str(path_mp4),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        str(norm_path),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Crossfade 0.3s between opener and path explainer
    fade_dur = 0.3
    offset = max(opener_dur - fade_dur, 0)
    total_video = opener_dur + path_dur - fade_dur
    print(f">>> compositing with {fade_dur}s crossfade — total ~{total_video:.2f}s")

    # xfade for video. For audio, we just keep the path-explainer's audio
    # delayed by (opener_dur - fade_dur) so it lines up with the crossfade.
    subprocess.run([
        ffmpeg, "-y",
        "-i", str(norm_opener),
        "-i", str(norm_path),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={fade_dur}:offset={offset:.3f}[v];"
        f"[1:a]adelay={int(offset * 1000)}|{int(offset * 1000)}[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(out),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Clean up intermediate files
    norm_opener.unlink(missing_ok=True)
    norm_path.unlink(missing_ok=True)
    print(f"\n→ {out}")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: python composite.py <COUNTRY_CODE> <opener_mp4_path>")
    composite(sys.argv[1], Path(sys.argv[2]).expanduser().resolve())
