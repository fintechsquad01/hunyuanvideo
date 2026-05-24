"""Orchestrator: render silent video → synth audio → mux → final MP4."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import render_to_mp4  # noqa: E402
from audio import synth_local, synth_elevenlabs  # noqa: E402

import os

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"


def build(use_elevenlabs: bool | None = None) -> Path:
    OUT.mkdir(exist_ok=True)

    silent = OUT / "wc_champions_pantheon_silent.mp4"
    audio_wav = OUT / "wc_champions_pantheon_audio.wav"
    final = OUT / "wc_champions_pantheon.mp4"

    print("==> Rendering frames")
    render_to_mp4(silent)

    print("==> Synthesizing audio")
    if use_elevenlabs is None:
        use_elevenlabs = bool(os.environ.get("ELEVENLABS_API_KEY"))
    if use_elevenlabs:
        synth_elevenlabs(audio_wav)
    else:
        synth_local(audio_wav)

    print("==> Muxing")
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(silent),
            "-i", str(audio_wav),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(final),
        ],
        check=True,
    )
    print(f"\n✓ {final} ({final.stat().st_size / 1024 / 1024:.2f} MB)")
    return final


if __name__ == "__main__":
    build()
