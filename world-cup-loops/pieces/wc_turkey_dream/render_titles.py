"""Render the two title cards as MP4 (intro + outro) using PIL + ffmpeg.

Runs locally, no MCP, no credits. Outputs:
  output/wc_turkey_t01_title.mp4  (5s, Turkish-red bg, "TÜRKİYE 2026 / BİR HAYAL · A DREAM")
  output/wc_turkey_t02_outro.mp4  (6s, black bg, "Turkey didn't qualify for WC2026. But we can dream.")

Resolution matches the AI scenes (768x1344, 9:16, 30fps).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 768, 1344, 30
OUT_DIR = Path(__file__).resolve().parents[2] / "output"
OUT_DIR.mkdir(exist_ok=True)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try a few common system fonts; fall back to PIL default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def _center(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, text: str, y: int, fill: tuple[int, int, int]) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=font, fill=fill)


def render_card(headline: str, subhead: str, bg_hex: str, accent_hex: str, out_png: Path) -> None:
    bg = tuple(int(bg_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    accent = tuple(int(accent_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    head_font = _load_font(96)
    sub_font = _load_font(46)
    tag_font = _load_font(30)

    # Soft top-of-frame crescent silhouette stamp (purely decorative)
    cx, cy, r = W // 2, H // 4, 60
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=accent, width=4)
    d.ellipse((cx - r + 24, cy - r, cx + r + 24, cy + r), fill=bg)

    # Center block
    _center(d, head_font, headline, H // 2 - 140, accent)
    _center(d, sub_font, subhead, H // 2 + 20, accent)

    # Footer tag
    _center(d, tag_font, "pitch.predict", H - 90, accent)

    img.save(out_png, "PNG")


def png_to_mp4(png: Path, mp4: Path, seconds: int) -> None:
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-framerate", str(FPS), "-t", str(seconds),
        "-i", str(png),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-vf", f"scale={W}:{H}",
        str(mp4),
    ]
    subprocess.run(cmd, check=True)


def render_all() -> dict[str, Path]:
    out: dict[str, Path] = {}

    intro_png = OUT_DIR / "wc_turkey_t01_title.png"
    intro_mp4 = OUT_DIR / "wc_turkey_t01_title.mp4"
    render_card("TÜRKİYE 2026", "BİR HAYAL · A DREAM", "#aa0d1a", "#ffffff", intro_png)
    png_to_mp4(intro_png, intro_mp4, 5)
    out["t01_title"] = intro_mp4

    outro_png = OUT_DIR / "wc_turkey_t02_outro.png"
    outro_mp4 = OUT_DIR / "wc_turkey_t02_outro.mp4"
    render_card("Turkey didn't qualify", "But we can dream.", "#0a0a0a", "#aa0d1a", outro_png)
    png_to_mp4(outro_png, outro_mp4, 6)
    out["t02_outro"] = outro_mp4

    return out


if __name__ == "__main__":
    paths = render_all()
    for k, v in paths.items():
        print(f"{k}: {v}")
