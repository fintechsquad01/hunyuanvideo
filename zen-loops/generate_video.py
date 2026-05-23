"""CLI entry point: render a video from a JSON config recipe.

Usage:
    python generate_video.py --config configs/bouncing_focus_01.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import imageio.v2 as imageio
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from engines.python_numpy.bouncing_spheres import BouncingSpheresEngine  # noqa: E402
from engines.python_numpy.marble_drop import MarbleDropEngine  # noqa: E402
from overlays.text_overlay import apply_overlay  # noqa: E402

ENGINES = {
    "bouncing_spheres": BouncingSpheresEngine,
    "marble_drop": MarbleDropEngine,
}


def render(cfg_path: Path) -> Path:
    cfg = json.loads(cfg_path.read_text())
    archetype = cfg["archetype"]
    if archetype not in ENGINES:
        raise SystemExit(f"unknown archetype: {archetype}")

    engine = ENGINES[archetype](cfg)
    overlay = cfg.get("overlay") or {}
    hook = overlay.get("hook_text")
    cta = overlay.get("cta_text")

    out_dir = REPO_ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{cfg['id']}.mp4"

    writer = imageio.get_writer(
        out_path,
        fps=cfg["fps"],
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=1,
    )
    try:
        for img in engine:
            img = apply_overlay(img, hook, cta)
            writer.append_data(np.array(img))
    finally:
        writer.close()
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, type=Path)
    args = p.parse_args()
    out = render(args.config)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
