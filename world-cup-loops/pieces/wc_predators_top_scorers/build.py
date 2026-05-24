"""Orchestrator for Predators of the Goal."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib.fal_image import fal_still  # noqa: E402
from _lib.tts import narrate, synth_music_bed, mix_to_wav  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import FAL_PROMPT, NARRATION_OPEN, NARRATION_CLOSE, SCORERS  # noqa: E402
from render import render_to_mp4, TOTAL_S, REVEAL_START, REVEAL_END, FPS, N_ROWS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"


def build() -> Path:
    OUT.mkdir(exist_ok=True)
    print("==> [1/4] fal backdrop (lion at golden hour)")
    backdrop = fal_still(FAL_PROMPT, OUT / "wc_predators_top_scorers_backdrop.png")

    print("==> [2/4] Silent render")
    silent = OUT / "wc_predators_top_scorers_silent.mp4"
    render_to_mp4(silent, backdrop)

    print("==> [3/4] Audio")
    # 6 row-reveal accents + final halo accent
    span = REVEAL_END - REVEAL_START
    accents = [(REVEAL_START + int(i * span / N_ROWS)) / FPS for i in range(N_ROWS)]
    accents.append(REVEAL_END / FPS + 0.4)
    bed = synth_music_bed(OUT / "wc_predators_top_scorers_bed.wav",
                          total_s=TOTAL_S, accent_times_s=accents)
    nar_open = narrate(NARRATION_OPEN, OUT / "wc_predators_top_scorers_open.wav",
                       fallback_seconds=2.5)
    nar_close = narrate(NARRATION_CLOSE, OUT / "wc_predators_top_scorers_close.wav",
                        fallback_seconds=2.5)
    audio = mix_to_wav(
        OUT / "wc_predators_top_scorers_audio.wav",
        [(bed, 0.0, 1.0),
         (nar_open, 0.1, 1.5),
         (nar_close, 11.5, 1.5)],
    )

    print("==> [4/4] Mux")
    final = OUT / "wc_predators_top_scorers.mp4"
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
