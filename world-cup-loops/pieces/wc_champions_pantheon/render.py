"""Render the trophy-cascade animation frame-by-frame and pipe to ffmpeg.

Produces a silent 1080x1920 30fps MP4. Audio is muxed in by build.py.

Pure Pillow + ffmpeg. No network, no AI in this layer — data is rendered
deterministically per the pitch-predict brand contract.
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path
from typing import Iterator

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import WINNERS, COLUMNS, tally  # noqa: E402

# Canvas
W, H = 1080, 1920
FPS = 30

# Timing (frame indices)
HOOK_END = 60          # 0:00 – 0:02
BUILD_END = 180        # 0:02 – 0:06   (6 drops, 1930–1958)
CLIMB_END = 330        # 0:06 – 0:11   (16 drops, 1962–2022)
PEAK_END = 390         # 0:11 – 0:13
TOTAL = 420            # 0:14

# Layout
TOP_BAND_H = 280
COL_LABEL_BAND_H = 120
PEAK_LABEL_BAND_H = 220
CTA_BAND_H = 200

N_COLS = 8
COL_W = 100
COL_GAP = 20
COLS_TOTAL_W = N_COLS * COL_W + (N_COLS - 1) * COL_GAP   # 940
COLS_X0 = (W - COLS_TOTAL_W) // 2                         # 70

# Trophy glyph
TROPHY_H = 64
TROPHY_W = 56
TROPHY_VGAP = 8

# Colors
BG_TOP = (13, 40, 24)
BG_BOTTOM = (8, 24, 14)
GOLD = (255, 212, 0)
GOLD_DIM = (180, 145, 0)
WHITE = (255, 255, 255)
SECONDARY = (217, 230, 223)
INACTIVE = (90, 106, 96)
PITCH = (10, 70, 28)


def _load_font(size: int, kind: str = "bold") -> ImageFont.FreeTypeFont:
    """Best-effort font loader. Anton/Inter aren't installed in most envs;
    DejaVuSans-Bold + Condensed are the universal fallbacks."""
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    candidates_cond = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf",
    ]
    paths = candidates_cond if kind == "cond" else candidates_bold
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _gradient_bg() -> Image.Image:
    """Vertical gradient pitch background, generated once and reused."""
    bg = Image.new("RGB", (W, H), BG_TOP)
    px = bg.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return bg


def _col_center_x(i: int) -> int:
    return COLS_X0 + i * (COL_W + COL_GAP) + COL_W // 2


def _col_base_y() -> int:
    return H - CTA_BAND_H - COL_LABEL_BAND_H - 40


def _col_top_y() -> int:
    return TOP_BAND_H + 60


def _draw_trophy(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0, glow: float = 0.0) -> None:
    """Pillow-drawn gold trophy glyph (no FIFA mark)."""
    w = int(TROPHY_W * scale)
    h = int(TROPHY_H * scale)
    color = GOLD
    if glow > 0:
        color = (255, min(255, 212 + int(43 * glow)), int(80 * glow))
    # cup body (trapezoid)
    cup_top = cy - h // 2 + int(h * 0.05)
    cup_bot = cy + int(h * 0.18)
    cup_top_w = int(w * 0.85)
    cup_bot_w = int(w * 0.55)
    draw.polygon(
        [
            (cx - cup_top_w // 2, cup_top),
            (cx + cup_top_w // 2, cup_top),
            (cx + cup_bot_w // 2, cup_bot),
            (cx - cup_bot_w // 2, cup_bot),
        ],
        fill=color,
    )
    # handles (two arcs)
    handle_y = cup_top + (cup_bot - cup_top) // 2
    handle_r = int(w * 0.20)
    draw.ellipse(
        [cx - cup_top_w // 2 - handle_r, handle_y - handle_r // 2,
         cx - cup_top_w // 2 + handle_r // 2, handle_y + handle_r // 2 + 2],
        outline=color, width=max(2, int(3 * scale)),
    )
    draw.ellipse(
        [cx + cup_top_w // 2 - handle_r // 2, handle_y - handle_r // 2,
         cx + cup_top_w // 2 + handle_r, handle_y + handle_r // 2 + 2],
        outline=color, width=max(2, int(3 * scale)),
    )
    # stem
    stem_w = int(w * 0.18)
    stem_top = cup_bot
    stem_bot = cy + int(h * 0.32)
    draw.rectangle([cx - stem_w // 2, stem_top, cx + stem_w // 2, stem_bot], fill=color)
    # base
    base_w = int(w * 0.65)
    base_h = int(h * 0.10)
    draw.rectangle([cx - base_w // 2, stem_bot, cx + base_w // 2, stem_bot + base_h], fill=color)


def _draw_text_centered(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, cy: int, fill, cx: int = W // 2) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2), text, font=font, fill=fill)


def _drop_schedule() -> list[tuple[int, str, int]]:
    """Return list of (frame_index_of_drop_start, country_code, drop_index_in_country).

    Distributes 22 trophy drops across BUILD (6) and CLIMB (16) windows.
    """
    schedule: list[tuple[int, str, int]] = []
    seen: dict[str, int] = {}
    # 6 drops across HOOK_END..BUILD_END (120 frames). One every 20 frames.
    for idx, (year, code) in enumerate(WINNERS[:6]):
        f = HOOK_END + idx * 20
        seen[code] = seen.get(code, 0) + 1
        schedule.append((f, code, seen[code]))
    # 16 drops across BUILD_END..CLIMB_END (150 frames). One every 9.375 frames.
    for idx, (year, code) in enumerate(WINNERS[6:]):
        f = BUILD_END + int(idx * 150 / 16)
        seen[code] = seen.get(code, 0) + 1
        schedule.append((f, code, seen[code]))
    return schedule


SCHEDULE = _drop_schedule()


def _year_at(frame: int) -> str:
    """The year ticker text at this frame."""
    if frame < HOOK_END:
        return "1930"
    if frame >= CLIMB_END:
        return "1930 — 2022"
    # find latest drop year at or before this frame
    last_year = WINNERS[0][0]
    for i, (drop_f, _, _) in enumerate(SCHEDULE):
        if drop_f <= frame:
            last_year = WINNERS[i][0]
        else:
            break
    return str(last_year)


def _trophy_state_at(frame: int) -> list[list[float]]:
    """For each column, return a list of 'placed' float [0..1] for each trophy.
    1.0 means fully placed. 0.0..1.0 means mid-drop animation (falling)."""
    drop_anim_frames = 16  # how long a drop takes
    state: dict[str, list[float]] = {c: [] for c in COLUMNS}
    for (drop_f, code, _) in SCHEDULE:
        if frame < drop_f:
            continue
        progress = min(1.0, (frame - drop_f) / drop_anim_frames)
        state[code].append(progress)
    return [state[c] for c in COLUMNS]


def _first_seen_at(frame: int) -> set[str]:
    """Set of country codes that have at least one trophy by this frame."""
    seen = set()
    for (drop_f, code, _) in SCHEDULE:
        if frame >= drop_f:
            seen.add(code)
    return seen


def _glow_at(frame: int) -> dict[str, float]:
    """Per-column glow intensity 0..1 for recent drops + sustained peak halo."""
    glow: dict[str, float] = {c: 0.0 for c in COLUMNS}
    decay = 10  # frames
    for (drop_f, code, _) in SCHEDULE:
        if drop_f <= frame < drop_f + decay:
            glow[code] = max(glow[code], 1.0 - (frame - drop_f) / decay)
    if frame >= CLIMB_END:
        # Champion sustained halo
        glow["BRA"] = max(glow["BRA"], 0.6)
    return glow


def _ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def render_frame(frame: int, bg: Image.Image) -> Image.Image:
    img = bg.copy()
    draw = ImageDraw.Draw(img, "RGBA")

    f_hook = _load_font(72, "bold")
    f_year = _load_font(96, "cond")
    f_col_label = _load_font(38, "cond")
    f_tally_value = _load_font(40, "cond")
    f_sub = _load_font(36, "bold")
    f_cta = _load_font(64, "bold")
    f_source = _load_font(24, "bold")
    f_watermark = _load_font(24, "bold")

    # --- top band: hook + year ticker ---
    _draw_text_centered(draw, "WHO HAS WON IT MOST?", f_hook, cy=80, fill=WHITE)
    # year ticker — fades in over hook, locks at peak
    year_text = _year_at(frame)
    year_alpha = 255 if frame >= 10 else int(255 * frame / 10)
    _draw_text_centered(draw, year_text, f_year, cy=200, fill=(*SECONDARY, year_alpha)[:3])

    # --- columns ---
    base_y = _col_base_y()
    top_y = _col_top_y()
    states = _trophy_state_at(frame)
    seen = _first_seen_at(frame)
    glows = _glow_at(frame)
    final_tally = tally()

    for i, code in enumerate(COLUMNS):
        cx = _col_center_x(i)

        # Column guide line (thin pitch-marking)
        draw.line([(cx, top_y + 40), (cx, base_y - 6)], fill=PITCH, width=2)

        # Column base label
        label_color = WHITE if code in seen else INACTIVE
        _draw_text_centered(draw, code, f_col_label, cy=base_y + 50, fill=label_color, cx=cx)

        # Trophies
        trophies = states[i]
        glow = glows[code]
        for ti, progress in enumerate(trophies):
            placed_y = base_y - ti * (TROPHY_H + TROPHY_VGAP) - TROPHY_H // 2
            # Falling animation: start from top_y, ease to placed_y
            start_y = top_y
            current_y = int(start_y + (placed_y - start_y) * _ease_out(progress))
            scale = 0.85 + 0.15 * progress
            _draw_trophy(draw, cx, current_y, scale=scale, glow=(glow if ti == len(trophies) - 1 else 0.0))

    # --- peak label + final tally ---
    if frame >= CLIMB_END:
        peak_progress = min(1.0, (frame - CLIMB_END) / 18)
        sub_alpha = int(255 * peak_progress)
        # "8 NATIONS. 22 TROPHIES." sub-label
        _draw_text_centered(
            draw, "8 NATIONS · 22 TROPHIES",
            f_sub, cy=base_y + 130, fill=(*SECONDARY, sub_alpha)[:3],
        )

    # Final tally row (only appears at peak)
    if frame >= CLIMB_END + 6:
        prog = min(1.0, (frame - CLIMB_END - 6) / 18)
        # render a left-to-right wipe by drawing tally items progressively
        items = [(c, final_tally[c]) for c in COLUMNS]
        # draw each item under its column
        for i, (code, n) in enumerate(items):
            cx = _col_center_x(i)
            # value below the country code
            value_color = GOLD if i == 0 else WHITE
            value_alpha = int(255 * prog)
            _draw_text_centered(
                draw, str(n), f_tally_value, cy=base_y + 100, fill=(*value_color, value_alpha)[:3], cx=cx,
            )

    # --- CTA + source + watermark ---
    if frame >= PEAK_END - 6:
        prog = min(1.0, (frame - PEAK_END + 6) / 24)
        alpha = int(255 * prog)
        _draw_text_centered(draw, "PICK YOUR CHAMPION", f_cta, cy=H - 110, fill=(*WHITE, alpha)[:3])
        _draw_text_centered(draw, "Source: FIFA · 1930–2022", f_source, cy=H - 50, fill=(*SECONDARY, alpha)[:3])

    # Watermark always on
    draw.text((30, H - 50), "pitch.predict", font=f_watermark, fill=SECONDARY)

    return img


def render_to_mp4(out_path: Path) -> Path:
    out_path.parent.mkdir(exist_ok=True, parents=True)
    bg = _gradient_bg()

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-level", "4.0",
        "-preset", "medium", "-crf", "20",
        str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for f in range(TOTAL):
            img = render_frame(f, bg)
            proc.stdin.write(img.tobytes())
            if f % 30 == 0:
                print(f"  frame {f}/{TOTAL}", flush=True)
    finally:
        proc.stdin.close()
        proc.wait()
    return out_path


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "output" / "wc_champions_pantheon_silent.mp4"
    render_to_mp4(out)
    print(f"Wrote {out} ({out.stat().st_size / 1024:.1f} KB)")
