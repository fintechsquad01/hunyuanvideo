"""Render the marble-orbits generative-art loop (silent)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import imageio.v2 as imageio
import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "world-cup-loops"))

from wc_engines.marble_orbits_art import MarbleOrbitsArtEngine  # noqa: E402


def main():
    cfg = json.loads((HERE / "config.json").read_text())
    out_dir = HERE.parent.parent / "output"
    out_dir.mkdir(exist_ok=True, parents=True)

    print(">>> marble orbits art engine")
    engine = MarbleOrbitsArtEngine(cfg, seed=11)
    print(f"    {engine.num_frames} frames @ {engine.fps}fps = {engine.duration}s")

    out_path = out_dir / "wc_marble_orbits_art.mp4"
    writer = imageio.get_writer(out_path, fps=cfg["fps"],
                                 codec="libx264", pixelformat="yuv420p",
                                 macro_block_size=1, quality=8)
    t0 = time.time()
    try:
        for i, img in enumerate(engine):
            writer.append_data(np.array(img))
            if i % 30 == 0:
                print(f"  frame {i}/{engine.num_frames}", flush=True)
    finally:
        writer.close()
    print(f"\nDONE — {out_path}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
