"""Shared brand chrome + Pillow helpers for pitch.predict video pieces.

Loads brand fonts from world-cup-loops/design/project/fonts and exposes
color tokens from colors_and_type.css. Every piece's renderer imports
from here so the visual language stays consistent.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "design" / "project" / "fonts"

# Canvas
W, H = 1080, 1920
FPS = 30

# Color tokens (from world-cup-loops/design/project/colors_and_type.css)
BG_TOP = (13, 40, 24)
BG_MID = (8, 24, 14)
BG_BOTTOM = (2, 10, 5)
GOLD = (255, 212, 0)
GOLD_DEEP = (212, 174, 0)
GREEN_BRIGHT = (26, 197, 116)
RED = (255, 77, 77)
WHITE = (255, 255, 255)
FG2 = (217, 230, 223)
FG3 = (138, 161, 149)
FG_MUTE = (90, 111, 100)
LINE = (255, 255, 255, 26)

# Type scale
FS_HOOK_XL = 72
FS_HOOK = 56
FS_WINNER = 140
FS_BANNER = 84
FS_NUM_XL = 64
FS_NUM = 40
FS_BADGE = 28
FS_BODY = 22
FS_FINE = 16

BAND_TOP_H = int(H * 0.07)
BAND_BOTTOM_H = int(H * 0.07)
WATERMARK_PAD = 24

_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(family: str, size: int) -> ImageFont.FreeTypeFont:
    """family in {anton, bebas, cond, cond_reg, inter_bold, inter_med}."""
    key = (family, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    paths_by_family = {
        "anton":      [FONT_DIR / "Anton-Regular.ttf"],
        "bebas":      [FONT_DIR / "BebasNeue-Regular.ttf"],
        "cond":       [FONT_DIR / "RobotoCondensed-Bold.ttf"],
        "cond_reg":   [FONT_DIR / "RobotoCondensed.ttf"],
        "inter_bold": [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
                       Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")],
        "inter_med":  [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                       Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")],
    }
    for p in paths_by_family.get(family, []):
        if p.exists():
            f = ImageFont.truetype(str(p), size)
            _FONT_CACHE[key] = f
            return f
    f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


def gradient_bg() -> Image.Image:
    """Brand pitch-gradient. Used when no fal backdrop is available."""
    bg = Image.new("RGB", (W, H), BG_TOP)
    px = bg.load()
    mid_y = int(H * 0.55)
    for y in range(H):
        if y <= mid_y:
            t = y / mid_y
            c1, c2 = BG_TOP, BG_MID
        else:
            t = (y - mid_y) / (H - mid_y - 1)
            c1, c2 = BG_MID, BG_BOTTOM
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return bg


def load_backdrop(path: Path | None) -> Image.Image:
    """Load a fal-generated still (or fallback)."""
    if path and path.exists():
        img = Image.open(path).convert("RGB")
        if img.size != (W, H):
            img = img.resize((W, H), Image.LANCZOS)
        # Apply a subtle dark gradient at top + bottom to seat the chrome
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        # darken top 22% + bottom 22% for text legibility
        for y in range(int(H * 0.22)):
            t = y / (H * 0.22)
            d.line([(0, y), (W, y)], fill=(0, 0, 0, int(180 * (1 - t))))
        for y in range(int(H * 0.22)):
            yy = H - 1 - y
            t = y / (H * 0.22)
            d.line([(0, yy), (W, yy)], fill=(0, 0, 0, int(180 * (1 - t))))
        return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return gradient_bg()


def draw_text_centered(draw: ImageDraw.ImageDraw, text: str,
                       fnt: ImageFont.FreeTypeFont, cy: int, fill,
                       cx: int = W // 2) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - bbox[1]), text, font=fnt, fill=fill)


def draw_hook_band(draw: ImageDraw.ImageDraw, text: str, alpha: int = 255) -> None:
    """Top 7% band with translucent black + ALL CAPS Inter Bold hook."""
    band_h = BAND_TOP_H
    overlay = Image.new("RGBA", (W, band_h), (0, 0, 0, int(160 * (alpha / 255))))
    # we draw via the existing draw context (assumes RGBA image)
    draw.rectangle([0, 0, W, band_h], fill=(0, 0, 0, int(160 * (alpha / 255))))
    f = font("inter_bold", FS_HOOK)
    draw_text_centered(draw, text, f, cy=band_h // 2, fill=(*WHITE, alpha)[:3])


def draw_cta_band(draw: ImageDraw.ImageDraw, text: str, alpha: int = 255,
                  cta_font: str = "anton", cta_size: int = 76) -> None:
    band_h = BAND_BOTTOM_H
    draw.rectangle([0, H - band_h, W, H], fill=(0, 0, 0, int(180 * (alpha / 255))))
    f = font(cta_font, cta_size)
    draw_text_centered(draw, text, f, cy=H - band_h // 2, fill=(*WHITE, alpha)[:3])


def draw_watermark(draw: ImageDraw.ImageDraw, position: str = "tl") -> None:
    f = font("inter_med", FS_FINE)
    if position == "tl":
        draw.text((WATERMARK_PAD, WATERMARK_PAD), "pitch.predict", font=f, fill=FG3)
    else:
        draw.text((W - WATERMARK_PAD - 110, H - WATERMARK_PAD - 14), "pitch.predict", font=f, fill=FG3)


def draw_source_line(draw: ImageDraw.ImageDraw, text: str, alpha: int = 200) -> None:
    f = font("inter_med", FS_FINE)
    draw_text_centered(draw, text, f, cy=H - BAND_BOTTOM_H - 22, fill=(*FG3, alpha)[:3])


def ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * (1 - 2 * t) ** 3 if t < 0.5 else 0.5 + 0.5 * (2 * t - 1) ** 3
