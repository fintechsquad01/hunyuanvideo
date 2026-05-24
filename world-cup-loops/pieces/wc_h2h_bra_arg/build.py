"""Orchestrator for the BRA vs ARG H2H piece."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib.fal_image import fal_still  # noqa: E402
from _lib.tts import narrate, synth_music_bed, mix_to_wav  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import FAL_PROMPT, NARRATION_OPEN, NARRATION_CLOSE  # noqa: E402
from render import render_to_mp4, TOTAL_S, COUNTER_END, FPS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"


def build() -> Path:
    OUT.mkdir(exist_ok=True)
    print("==> [1/4] fal backdrop (two big cats at golden hour)")
    backdrop = fal_still(FAL_PROMPT, OUT / "wc_h2h_bra_arg_backdrop.png")

    print("==> [2/4] Silent render")
    silent = OUT / "wc_h2h_bra_arg_silent.mp4"
    render_to_mp4(silent, backdrop)

    print("==> [3/4] Audio")
    # Two emotional accents: counter peak at 10s, lead reveal at 11s
    accent_times = [2.0, 4.0, 6.0, 8.0, COUNTER_END / FPS, COUNTER_END / FPS + 1.5]
    bed = synth_music_bed(OUT / "wc_h2h_bra_arg_bed.wav",
                          total_s=TOTAL_S, accent_times_s=accent_times)
    nar_open = narrate(NARRATION_OPEN, OUT / "wc_h2h_bra_arg_open.wav",
                       fallback_seconds=2.5)
    nar_close = narrate(NARRATION_CLOSE, OUT / "wc_h2h_bra_arg_close.wav",
                        fallback_seconds=2.5)
    audio = mix_to_wav(
        OUT / "wc_h2h_bra_arg_audio.wav",
        [(bed, 0.0, 1.0),
         (nar_open, 0.1, 1.5),
         (nar_close, 10.5, 1.5)],
    )

    print("==> [4/4] Mux")
    final = OUT / "wc_h2h_bra_arg.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(silent), "-i", str(audio),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(final)], check=True,
    )
    print(f"\n✓ {final} ({final.stat().st_size / 1024:.1f} KB)")
    return final


if __name__ == "__main__":
    build()
