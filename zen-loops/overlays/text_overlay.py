"""Engine-agnostic text overlay layer.

Applies hook text near the top and CTA text near the bottom of any PIL Image.
Works on output from any base engine (Unity render, NumPy sim, AI-video clip).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in [
        _FONT_DIR / "Inter-Bold.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def apply_overlay(img: Image.Image, hook_text: str | None, cta_text: str | None) -> Image.Image:
    draw = ImageDraw.Draw(img)
    w, h = img.size

    if hook_text:
        font = _load_font(72)
        tw, th = _text_size(draw, hook_text, font)
        x = (w - tw) // 2
        y = int(h * 0.08)
        draw.text(
            (x, y),
            hook_text,
            font=font,
            fill="white",
            stroke_width=4,
            stroke_fill="black",
        )

    if cta_text:
        font = _load_font(56)
        tw, th = _text_size(draw, cta_text, font)
        x = (w - tw) // 2
        y = int(h * 0.86)
        draw.text(
            (x, y),
            cta_text,
            font=font,
            fill="white",
            stroke_width=3,
            stroke_fill="black",
        )

    return img
