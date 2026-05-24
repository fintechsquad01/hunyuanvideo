"""Orchestrator for the Mountains of 2026 piece."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib.fal_image import fal_still  # noqa: E402
from _lib.tts import narrate, synth_music_bed, mix_to_wav  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import FAL_PROMPT, NARRATION_OPEN, NARRATION_CLOSE, VENUES  # noqa: E402
from render import render_to_mp4, FPS, REVEAL_END, HOOK_END, TOTAL_S  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"


def build() -> Path:
    OUT.mkdir(exist_ok=True)
    print("==> [1/4] fal backdrop")
    backdrop = fal_still(FAL_PROMPT, OUT / "wc_mountains_2026_backdrop.png")

    print("==> [2/4] Silent render")
    silent = OUT / "wc_mountains_2026_silent.mp4"
    render_to_mp4(silent, backdrop)

    print("==> [3/4] Audio: music bed + open/close narration")
    # Each bar reveals on a stagger; place an accent at each bar's pop time
    span = REVEAL_END - HOOK_END
    accents = [
        (HOOK_END + int(i * span * 0.62 / max(1, len(VENUES) - 1))) / FPS
        for i in range(len(VENUES))
    ]
    bed = synth_music_bed(OUT / "wc_mountains_2026_bed.wav",
                          total_s=TOTAL_S, accent_times_s=accents)
    nar_open = narrate(NARRATION_OPEN, OUT / "wc_mountains_2026_open.wav",
                       fallback_seconds=2.5)
    nar_close = narrate(NARRATION_CLOSE, OUT / "wc_mountains_2026_close.wav",
                        fallback_seconds=2.5)
    audio = mix_to_wav(
        OUT / "wc_mountains_2026_audio.wav",
        [(bed, 0.0, 1.0),
         (nar_open, 0.1, 1.5),
         (nar_close, 10.5, 1.5)],
    )

    print("==> [4/4] Mux")
    final = OUT / "wc_mountains_2026.mp4"
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
