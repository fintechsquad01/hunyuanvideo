"""Engine-agnostic text overlay layer.

Applies hook text near the top and CTA text near the bottom of any PIL Image.
Auto-shrinks font size to fit the canvas width and strips characters the
loaded font cannot render (e.g. emoji on a non-emoji-capable font).
"""

from __future__ import annotations

import unicodedata
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


def _sanitize(text: str) -> str:
    """Drop characters PIL's default fonts can't render (emoji, symbols).

    Keeps letters, digits, punctuation, and basic whitespace. Replaces
    stripped emojis with a trailing exclamation so the line still reads
    energetically.
    """
    out = []
    dropped = False
    for ch in text:
        cat = unicodedata.category(ch)
        if cat[0] in ("L", "N", "P", "Z") or ch in (" ", "-", "'"):
            out.append(ch)
        else:
            dropped = True
    cleaned = "".join(out).rstrip()
    if dropped and not cleaned.endswith(("!", "?", ".")):
        cleaned += "!"
    return cleaned


def _fit_font(text: str, max_w: int, start_size: int, min_size: int = 28) -> ImageFont.FreeTypeFont:
    """Find the largest font size for `text` that fits in `max_w`."""
    size = start_size
    img = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(img)
    while size > min_size:
        font = _load_font(size)
        w, _ = _text_size(draw, text, font)
        if w <= max_w:
            return font
        size -= 4
    return _load_font(min_size)


def _draw_banded(
    img: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    y_top: int,
    band_alpha: int = 160,
):
    draw = ImageDraw.Draw(img)
    w, _ = img.size
    tw, th = _text_size(draw, text, font)

    pad_x, pad_y = 32, 16
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(band)
    bdraw.rectangle(
        [
            (w - tw) // 2 - pad_x,
            y_top - pad_y,
            (w + tw) // 2 + pad_x,
            y_top + th + pad_y,
        ],
        fill=(0, 0, 0, band_alpha),
    )
    img.paste(band, (0, 0), band)

    draw = ImageDraw.Draw(img)
    draw.text(
        ((w - tw) // 2, y_top),
        text,
        font=font,
        fill="white",
        stroke_width=3,
        stroke_fill="black",
    )


def apply_overlay(img: Image.Image, hook_text: str | None, cta_text: str | None) -> Image.Image:
    w, h = img.size
    safe_w = int(w * 0.88)

    if hook_text:
        clean = _sanitize(hook_text)
        if clean:
            font = _fit_font(clean, safe_w, start_size=84)
            _draw_banded(img, clean, font, y_top=int(h * 0.07))

    if cta_text:
        clean = _sanitize(cta_text)
        if clean:
            font = _fit_font(clean, safe_w, start_size=64)
            _draw_banded(img, clean, font, y_top=int(h * 0.84))

    return img
