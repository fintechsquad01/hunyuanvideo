"""v2 orchestrator: open hero → chart cascade → close hero, with audio.

  hero_open.mp4   (2.0s)   fal.ai still + narration  "Every World Cup. Every champion."
  chart.mp4       (14.0s)  deterministic Pillow render + music bed
  hero_close.mp4  (2.5s)   fal.ai still + narration  "Eight nations. Pick yours."

  -> wc_champions_pantheon_v2.mp4  (~18.5s)

Run locally for v2-with-fallbacks (no API keys), or from the GitHub
Actions runner with FAL_KEY + ELEVENLABS_API_KEY for the premium build.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import render_to_mp4  # noqa: E402
from audio import synth_local, synth_elevenlabs  # noqa: E402
from narration import narrate, CUES  # noqa: E402
from hero import build_open, build_close  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"


def build_v2() -> Path:
    OUT.mkdir(exist_ok=True)

    print("==> [1/5] Narration")
    nar_dir = OUT / "wc_champions_narration"
    nar_open = narrate(CUES["open"], nar_dir / "open.wav", fallback_seconds=2.0)
    nar_close = narrate(CUES["close"], nar_dir / "close.wav", fallback_seconds=2.5)

    print("==> [2/5] Heroes (fal.ai backdrops + overlay)")
    hero_dir = OUT / "wc_champions_pantheon_heroes"
    open_clip = build_open(hero_dir, nar_open)
    close_clip = build_close(hero_dir, nar_close)

    print("==> [3/5] Chart cascade")
    chart_silent = OUT / "wc_champions_pantheon_silent.mp4"
    render_to_mp4(chart_silent)
    chart_audio = OUT / "wc_champions_pantheon_audio.wav"
    if os.environ.get("ELEVENLABS_API_KEY"):
        synth_elevenlabs(chart_audio)
    else:
        synth_local(chart_audio)
    chart_clip = OUT / "wc_champions_pantheon_chart.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(chart_silent),
        "-i", str(chart_audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(chart_clip),
    ], check=True)

    print("==> [4/5] Concat open + chart + close")
    list_path = OUT / "wc_champions_pantheon_concat.txt"
    list_path.write_text(
        f"file '{open_clip}'\nfile '{chart_clip}'\nfile '{close_clip}'\n"
    )
    final = OUT / "wc_champions_pantheon_v2.mp4"
    # Re-encode through concat filter to be safe with mixed codecs/durations
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(open_clip),
        "-i", str(chart_clip),
        "-i", str(close_clip),
        "-filter_complex",
        "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(final),
    ], check=True)

    print(f"\n==> [5/5] Done: {final} ({final.stat().st_size / 1024 / 1024:.2f} MB)")
    return final


if __name__ == "__main__":
    build_v2()
