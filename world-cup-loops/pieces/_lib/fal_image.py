"""fal.ai still-image generation for backdrops.

  FLUX dev: cheap, photoreal-leaning, ~$0.025 per 1080×1920 image.

Falls back to a numpy-rendered placeholder (deep navy + god rays) if
FAL_KEY is missing or the call fails. Always returns a usable PNG.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Re-use canvas size from chrome.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
from chrome import W, H  # noqa: E402


def fal_still(prompt: str, out_path: Path, model: str = "fal-ai/flux/dev",
              width: int = W, height: int = H) -> Path:
    """Generate a still via fal-client. Needs FAL_KEY env var.

    Falls back to placeholder_still() on any failure.
    """
    if not os.environ.get("FAL_KEY"):
        print(f"  [fal] no FAL_KEY — placeholder for {out_path.name}")
        return placeholder_still(out_path)
    try:
        import fal_client  # type: ignore[import-not-found]
        print(f"  [fal] calling {model} for {out_path.name}")
        result = fal_client.subscribe(
            model,
            arguments={
                "prompt": prompt,
                "image_size": {"width": width, "height": height},
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
            },
        )
        url = result["images"][0]["url"]
        import urllib.request
        out_path.parent.mkdir(exist_ok=True, parents=True)
        with urllib.request.urlopen(url, timeout=180) as r:
            out_path.write_bytes(r.read())
        return out_path
    except Exception as e:
        print(f"  [fal] failed for {out_path.name}: {e!r} — placeholder")
        return placeholder_still(out_path)


def placeholder_still(out_path: Path) -> Path:
    """Deterministic cinematic fallback — looks intentional, not broken."""
    img = Image.new("RGB", (W, H), (4, 12, 8))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(13 * (1 - t) + 2 * t)
        g = int(40 * (1 - t) + 10 * t)
        b = int(24 * (1 - t) + 5 * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = W // 2, H // 2
    for r_out, alpha in [(900, 12), (700, 22), (500, 36), (320, 56), (180, 92)]:
        gdraw.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
                      fill=(255, 212, 0, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    out_path.parent.mkdir(exist_ok=True, parents=True)
    img.save(out_path, "PNG")
    return out_path
