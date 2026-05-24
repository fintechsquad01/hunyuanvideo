"""Generate opening + closing hero MP4 clips.

A hero clip = static cinematic image (preferably fal.ai-generated) +
overlay text in brand fonts + optional narration audio.

Locally (no FAL_KEY): falls back to a numpy/Pillow-rendered placeholder
still (deep navy + golden god rays).

On a runner with FAL_KEY: calls fal-ai/flux/dev (1080×1920) for a true
cinematic backdrop and composites the brand overlay on top.

Output: silent or audio-baked MP4 at the path provided.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import (  # noqa: E402
    W, H, FPS, _font, _draw_text_centered, WATERMARK_PAD,
    GOLD, GOLD_DEEP, WHITE, FG2, FG3, BAND_TOP_H, BAND_BOTTOM_H,
)

ROOT = Path(__file__).resolve().parents[2]


# --------- fal backdrop ---------

def generate_fal_still(prompt: str, out_path: Path) -> Path:
    """Call fal-client to generate a 1080×1920 still. Requires FAL_KEY in env.

    Returns out_path on success. Raises on failure (so caller can fall back).
    """
    import fal_client  # type: ignore[import-not-found]
    # FLUX dev is the workhorse: cheap, fast, photoreal-leaning
    result = fal_client.subscribe(
        "fal-ai/flux/dev",
        arguments={
            "prompt": prompt,
            "image_size": {"width": 1080, "height": 1920},
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
        },
    )
    url = result["images"][0]["url"]
    import urllib.request
    out_path.parent.mkdir(exist_ok=True, parents=True)
    with urllib.request.urlopen(url, timeout=120) as r:
        out_path.write_bytes(r.read())
    return out_path


def fallback_still(out_path: Path, kind: str = "open") -> Path:
    """Numpy/Pillow fallback when fal is unavailable. Looks intentional."""
    img = Image.new("RGB", (W, H), (4, 12, 8))
    # Vertical gradient deep navy → near-black
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(13 * (1 - t) + 2 * t)
        g = int(40 * (1 - t) + 10 * t)
        b = int(24 * (1 - t) + 5 * t)
        for x in range(W):
            px[x, y] = (r, g, b)

    # Add a centered radial gold glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = W // 2, H // 2 + (40 if kind == "open" else -40)
    for r_out, alpha in [(900, 12), (700, 22), (500, 36), (320, 56), (180, 92)]:
        gdraw.ellipse(
            [cx - r_out, cy - r_out, cx + r_out, cy + r_out],
            fill=(255, 212, 0, alpha),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    # Add subtle vertical god-rays
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(rays)
    for x in range(0, W, 90):
        rdraw.polygon(
            [(x, 0), (x + 8, 0), (x + 80, H), (x + 70, H)],
            fill=(255, 212, 0, 8),
        )
    rays = rays.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img.convert("RGBA"), rays).convert("RGB")

    out_path.parent.mkdir(exist_ok=True, parents=True)
    img.save(out_path, "PNG")
    return out_path


# --------- text overlay + clip render ---------

def render_hero_clip(
    still_path: Path,
    text_xl: str,
    text_sub: str,
    duration_s: float,
    out_path: Path,
    audio_wav: Path | None = None,
    fade_s: float = 0.4,
) -> Path:
    """Render an MP4 clip: still image with overlay text fading in/out.

    Optionally mux a narration WAV. Output 1080×1920 30fps.
    """
    base = Image.open(still_path).convert("RGB")
    if base.size != (W, H):
        base = base.resize((W, H), Image.LANCZOS)

    n_frames = int(duration_s * FPS)
    fade_n = int(fade_s * FPS)

    f_xl = _font("anton", 110)
    f_sub = _font("inter_bold", 32)
    f_watermark = _font("inter_med", 16)

    out_path.parent.mkdir(exist_ok=True, parents=True)
    tmp = out_path.with_suffix(".silent.mp4")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-level", "4.0",
        "-preset", "medium", "-crf", "20",
        str(tmp),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None

    try:
        for fi in range(n_frames):
            # Alpha curve: fade in then hold then fade out
            if fi < fade_n:
                alpha = fi / fade_n
            elif fi >= n_frames - fade_n:
                alpha = max(0.0, (n_frames - fi) / fade_n)
            else:
                alpha = 1.0
            a = int(255 * alpha)

            frame = base.copy()
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ldraw = ImageDraw.Draw(layer)

            # darken vignette top + bottom for text legibility
            ldraw.rectangle([0, 0, W, BAND_TOP_H + 220], fill=(0, 0, 0, int(160 * min(1, alpha + 0.2))))
            ldraw.rectangle([0, H - BAND_BOTTOM_H - 220, W, H], fill=(0, 0, 0, int(160 * min(1, alpha + 0.2))))

            # XL line — centered upper third
            xl_cy = int(H * 0.36)
            xl_w = ldraw.textlength(text_xl, font=f_xl)
            ldraw.text(((W - xl_w) // 2, xl_cy - 55), text_xl, font=f_xl, fill=(*WHITE, a))

            # Sub line — under XL
            sub_w = ldraw.textlength(text_sub, font=f_sub)
            ldraw.text(((W - sub_w) // 2, xl_cy + 80), text_sub, font=f_sub, fill=(*FG2, a))

            # Watermark
            ldraw.text((WATERMARK_PAD, WATERMARK_PAD), "pitch.predict", font=f_watermark, fill=(*FG3, 200))

            composed = Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")
            proc.stdin.write(composed.tobytes())
    finally:
        proc.stdin.close()
        proc.wait()

    if audio_wav and audio_wav.exists():
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(tmp), "-i", str(audio_wav),
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", str(out_path)],
            check=True,
        )
        tmp.unlink()
    else:
        tmp.rename(out_path)
    return out_path


# --------- top-level: produce open + close heroes ---------

OPEN_PROMPT = (
    "Cinematic photorealistic establishing shot, eight glowing golden football "
    "World Cup style trophies floating in a vast dark marble pantheon at night, "
    "dramatic warm golden god rays of light cutting through faint mist, "
    "deep navy and gold atmosphere, polished marble pedestals, soft particles "
    "drifting, no text, no logos, no faces, no FIFA branding, museum lighting, "
    "9:16 vertical composition, magical realism, breathtaking depth and scale."
)

CLOSE_PROMPT = (
    "Cinematic photorealistic hero shot, one massive central glowing golden "
    "football trophy with seven smaller trophies arranged behind it in cascading "
    "sizes inside a vast warm-lit marble hall, dramatic warm golden lighting "
    "from above, mist drifting at floor level, soft particles, deep navy and gold "
    "atmosphere, no text, no logos, no FIFA branding, no faces, 9:16 vertical "
    "composition, magical realism, ceremonial, triumphant."
)


def build_open(out_dir: Path, narration_wav: Path | None) -> Path:
    still = out_dir / "hero_open.png"
    try:
        if os.environ.get("FAL_KEY"):
            generate_fal_still(OPEN_PROMPT, still)
        else:
            fallback_still(still, "open")
    except Exception as e:
        print(f"  fal failed for open ({e!r}) — using fallback")
        fallback_still(still, "open")
    return render_hero_clip(
        still_path=still,
        text_xl="WHO HAS WON IT MOST?",
        text_sub="Every World Cup champion · 1930–2022",
        duration_s=2.0,
        out_path=out_dir / "hero_open.mp4",
        audio_wav=narration_wav,
    )


def build_close(out_dir: Path, narration_wav: Path | None) -> Path:
    still = out_dir / "hero_close.png"
    try:
        if os.environ.get("FAL_KEY"):
            generate_fal_still(CLOSE_PROMPT, still)
        else:
            fallback_still(still, "close")
    except Exception as e:
        print(f"  fal failed for close ({e!r}) — using fallback")
        fallback_still(still, "close")
    return render_hero_clip(
        still_path=still,
        text_xl="PICK YOUR CHAMPION",
        text_sub="BRA 5 · ITA 4 · GER 4 · ARG 3 · URU 2 · FRA 2 · ENG 1 · ESP 1",
        duration_s=2.5,
        out_path=out_dir / "hero_close.mp4",
        audio_wav=narration_wav,
    )


if __name__ == "__main__":
    out = ROOT / "output" / "wc_champions_pantheon_heroes"
    out.mkdir(exist_ok=True, parents=True)
    print("Building open hero…")
    o = build_open(out, None)
    print(f"  {o}")
    print("Building close hero…")
    c = build_close(out, None)
    print(f"  {c}")
