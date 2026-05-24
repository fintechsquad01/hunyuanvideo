"""Render the trophy-cascade animation per the pitch.predict design system.

Uses brand fonts shipped in `world-cup-loops/design/project/fonts/`.
Color tokens from `colors_and_type.css`.

Output: silent 1080×1920 30fps MP4 at output/wc_champions_pantheon_silent.mp4.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import WINNERS, COLUMNS, tally  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "design" / "project" / "fonts"

# Canvas
W, H = 1080, 1920
FPS = 30

# Timing
HOOK_END = 60
BUILD_END = 180
CLIMB_END = 330
PEAK_END = 390
TOTAL = 420

# Color tokens (from colors_and_type.css)
BG_TOP = (13, 40, 24)         # --pp-bg-top
BG_MID = (8, 24, 14)          # --pp-bg-mid
BG_BOTTOM = (2, 10, 5)        # --pp-bg-bottom
GOLD = (255, 212, 0)          # --pp-yellow
GOLD_DEEP = (212, 174, 0)     # --pp-yellow-deep
GREEN_BRIGHT = (26, 197, 116) # --pp-green-bright
RED = (255, 77, 77)           # --pp-red
WHITE = (255, 255, 255)       # --pp-fg
FG2 = (217, 230, 223)         # --pp-fg-2
FG3 = (138, 161, 149)         # --pp-fg-3
FG_MUTE = (90, 111, 100)      # --pp-fg-mute
LINE = (255, 255, 255, 26)    # --pp-line (10%)

# Per-country accent (their primary team color for the tally row)
COUNTRY_ACCENT = {
    "BRA": (253, 198, 17),
    "ITA": (0, 142, 67),
    "GER": (255, 200, 0),
    "ARG": (108, 188, 222),
    "URU": (88, 173, 255),
    "FRA": (0, 75, 154),
    "ENG": (255, 77, 77),
    "ESP": (255, 77, 77),
}

# Type sizes (from --pp-fs-* in colors_and_type.css, scaled for content)
FS_HOOK_XL = 72
FS_HOOK = 56
FS_WINNER = 140
FS_BANNER = 84
FS_NUM_XL = 64
FS_NUM = 40
FS_BADGE = 28
FS_BODY = 22
FS_FINE = 16

# Layout (7% band top/bottom per --pp-band-h)
BAND_TOP_H = int(H * 0.07)            # 134
BAND_BOTTOM_H = int(H * 0.07)         # 134
WATERMARK_PAD = 24

# Column geometry
N_COLS = 8
COL_W = 100
COL_GAP = 22
COLS_TOTAL_W = N_COLS * COL_W + (N_COLS - 1) * COL_GAP   # 954
COLS_X0 = (W - COLS_TOTAL_W) // 2                         # 63
COL_TOP_Y = 300              # below year ticker
COL_BASE_Y = 1500            # leave room for labels + bands
COL_LABEL_Y = 1540           # country code (BRA, ITA, ...)
COL_TALLY_Y = 1605           # number under code
COL_SUBLABEL_Y = 1685        # "8 NATIONS · 22 TROPHIES"

# Trophy glyph
TROPHY_H = 70
TROPHY_W = 60
TROPHY_VGAP = 10


# ----------------------- fonts -----------------------

_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _font(family: str, size: int) -> ImageFont.FreeTypeFont:
    """family in {anton, bebas, cond, cond_reg, inter_bold}."""
    key = (family, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    paths_by_family = {
        "anton": [FONT_DIR / "Anton-Regular.ttf"],
        "bebas": [FONT_DIR / "BebasNeue-Regular.ttf"],
        "cond": [FONT_DIR / "RobotoCondensed-Bold.ttf"],
        "cond_reg": [FONT_DIR / "RobotoCondensed.ttf"],
        "inter_bold": [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        ],
        "inter_med": [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        ],
    }
    for p in paths_by_family.get(family, []):
        if p.exists():
            f = ImageFont.truetype(str(p), size)
            _FONT_CACHE[key] = f
            return f
    f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


# ----------------------- background -----------------------

def _gradient_bg() -> Image.Image:
    """3-stop vertical gradient per --pp-pitch-gradient."""
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


# ----------------------- helpers -----------------------

def _col_center_x(i: int) -> int:
    return COLS_X0 + i * (COL_W + COL_GAP) + COL_W // 2


def _draw_text_centered(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, cy: int, fill, cx: int = W // 2) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # Pillow textbbox includes ascender padding; use (bbox[1]) to center on glyph baseline
    draw.text((cx - tw // 2, cy - th // 2 - bbox[1]), text, font=font, fill=fill)


def _ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def _ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * (1 - 2 * t) ** 3 if t < 0.5 else 0.5 + 0.5 * (2 * t - 1) ** 3


def _draw_trophy(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0, glow: float = 0.0) -> None:
    w = int(TROPHY_W * scale)
    h = int(TROPHY_H * scale)
    color = GOLD
    if glow > 0:
        color = (255, min(255, 212 + int(43 * glow)), min(255, int(80 * glow)))
    cup_top = cy - h // 2 + int(h * 0.04)
    cup_bot = cy + int(h * 0.18)
    cup_top_w = int(w * 0.85)
    cup_bot_w = int(w * 0.55)
    draw.polygon(
        [(cx - cup_top_w // 2, cup_top),
         (cx + cup_top_w // 2, cup_top),
         (cx + cup_bot_w // 2, cup_bot),
         (cx - cup_bot_w // 2, cup_bot)],
        fill=color,
    )
    handle_y = cup_top + (cup_bot - cup_top) // 2
    handle_r = int(w * 0.22)
    line_w = max(2, int(3 * scale))
    draw.ellipse(
        [cx - cup_top_w // 2 - handle_r, handle_y - handle_r // 2,
         cx - cup_top_w // 2 + handle_r // 2, handle_y + handle_r // 2 + 2],
        outline=color, width=line_w,
    )
    draw.ellipse(
        [cx + cup_top_w // 2 - handle_r // 2, handle_y - handle_r // 2,
         cx + cup_top_w // 2 + handle_r, handle_y + handle_r // 2 + 2],
        outline=color, width=line_w,
    )
    stem_w = int(w * 0.18)
    stem_top = cup_bot
    stem_bot = cy + int(h * 0.34)
    draw.rectangle([cx - stem_w // 2, stem_top, cx + stem_w // 2, stem_bot], fill=color)
    base_w = int(w * 0.65)
    base_h = int(h * 0.10)
    draw.rectangle([cx - base_w // 2, stem_bot, cx + base_w // 2, stem_bot + base_h], fill=color)


def _drop_schedule() -> list[tuple[int, str]]:
    sched: list[tuple[int, str]] = []
    for idx, (_, code) in enumerate(WINNERS[:6]):
        sched.append((HOOK_END + idx * 20, code))
    for idx, (_, code) in enumerate(WINNERS[6:]):
        sched.append((BUILD_END + int(idx * 150 / 16), code))
    return sched


SCHEDULE = _drop_schedule()


def _year_at(frame: int) -> str:
    if frame < HOOK_END:
        return "1930"
    if frame >= CLIMB_END:
        return "1930 — 2022"
    last_year = WINNERS[0][0]
    for i, (drop_f, _) in enumerate(SCHEDULE):
        if drop_f <= frame:
            last_year = WINNERS[i][0]
        else:
            break
    return str(last_year)


def _trophy_state_at(frame: int) -> dict[str, list[float]]:
    state: dict[str, list[float]] = {c: [] for c in COLUMNS}
    anim = 22  # frames per drop including bounce
    for (drop_f, code) in SCHEDULE:
        if frame >= drop_f:
            state[code].append(min(1.0, (frame - drop_f) / anim))
    return state


def _drop_curve(t: float) -> tuple[float, float]:
    """Return (y_progress 0..1, scale_factor) for drop animation.

    y_progress eases out with a small overshoot+settle for a bounce feel.
    scale punches up briefly on impact then settles to 1.0.
    """
    if t < 0.65:
        # Fall phase: ease out
        u = t / 0.65
        return (1 - (1 - u) ** 3, 0.85 + 0.10 * u)
    elif t < 0.85:
        # Overshoot phase: slight extra past the line
        u = (t - 0.65) / 0.20
        return (1.0 + 0.04 * (1 - u), 1.10 - 0.05 * u)
    else:
        # Settle to rest
        u = (t - 0.85) / 0.15
        return (1.0 + 0.04 * (1 - u) ** 2 - 0.04, 1.05 - 0.05 * u)


def _first_seen_at(frame: int) -> set[str]:
    return {code for (drop_f, code) in SCHEDULE if frame >= drop_f}


def _glow_at(frame: int) -> dict[str, float]:
    glow: dict[str, float] = {c: 0.0 for c in COLUMNS}
    decay = 14
    # Recent-drop flash (any column)
    for (drop_f, code) in SCHEDULE:
        if drop_f <= frame < drop_f + decay:
            glow[code] = max(glow[code], 1.0 - (frame - drop_f) / decay)
    # First-time-winner extra brightness (sustained 18 frames)
    seen_at: dict[str, int] = {}
    for (drop_f, code) in SCHEDULE:
        if code not in seen_at:
            seen_at[code] = drop_f
    first_decay = 22
    for code, f0 in seen_at.items():
        if f0 <= frame < f0 + first_decay:
            glow[code] = max(glow[code], 0.85 - 0.4 * (frame - f0) / first_decay)
    # PEAK halo on the actual leader (data-driven, not hard-coded)
    if frame >= CLIMB_END:
        leader = max(tally().items(), key=lambda kv: kv[1])[0]
        # Pulsing halo, slow LFO so it breathes
        import math
        pulse = 0.55 + 0.20 * math.sin((frame - CLIMB_END) * 0.18)
        glow[leader] = max(glow[leader], pulse)
    return glow


def _year_pulse(frame: int) -> float:
    """0..1 scale pulse triggered on the most recent year change."""
    decay = 8
    for (drop_f, _) in SCHEDULE:
        if drop_f <= frame < drop_f + decay:
            return 1.0 - (frame - drop_f) / decay
    return 0.0


# ----------------------- frame render -----------------------

def render_frame(frame: int, bg: Image.Image) -> Image.Image:
    img = bg.copy()
    draw = ImageDraw.Draw(img, "RGBA")

    f_hook = _font("inter_bold", FS_HOOK)
    f_year = _font("cond", FS_NUM_XL)
    f_year_lock = _font("cond", FS_NUM)
    f_col_label = _font("cond", 40)
    f_tally_value = _font("cond", FS_NUM)
    f_sublabel = _font("inter_bold", FS_BADGE)
    f_cta = _font("anton", 76)
    f_source = _font("inter_med", FS_FINE)
    f_watermark = _font("inter_med", FS_FINE)

    # --- top band (7% of H) ---
    draw.rectangle([0, 0, W, BAND_TOP_H], fill=(0, 0, 0, 120))
    _draw_text_centered(draw, "WHO HAS WON IT MOST?", f_hook, cy=BAND_TOP_H // 2, fill=WHITE)

    # --- year ticker ---
    year_cy = BAND_TOP_H + 80
    year_text = _year_at(frame)
    if frame >= CLIMB_END:
        # Locked range — render smaller and let "8 NATIONS · 22 TROPHIES" carry the eye
        _draw_text_centered(draw, "1930 — 2022", f_year_lock, cy=year_cy, fill=FG2)
    else:
        # Scale-pulse on each year change for visible movement
        pulse = _year_pulse(frame)
        pulse_size = FS_NUM_XL + int(18 * pulse)
        f_year_pulse = _font("cond", pulse_size)
        _draw_text_centered(draw, year_text, f_year_pulse, cy=year_cy, fill=WHITE)

    # --- columns + trophies ---
    states = _trophy_state_at(frame)
    seen = _first_seen_at(frame)
    glows = _glow_at(frame)

    for i, code in enumerate(COLUMNS):
        cx = _col_center_x(i)

        # Faint column guide line
        draw.line([(cx, COL_TOP_Y + 30), (cx, COL_BASE_Y - 8)], fill=LINE, width=2)

        # Country code at the base
        label_color = WHITE if code in seen else FG_MUTE
        _draw_text_centered(draw, code, f_col_label, cy=COL_LABEL_Y, fill=label_color, cx=cx)

        # Trophies (placed bottom-up)
        trophies = states[code]
        glow = glows[code]
        for ti, progress in enumerate(trophies):
            placed_y = COL_BASE_Y - ti * (TROPHY_H + TROPHY_VGAP) - TROPHY_H // 2
            y_prog, drop_scale = _drop_curve(progress)
            current_y = int(COL_TOP_Y + (placed_y - COL_TOP_Y) * y_prog)
            is_top = ti == len(trophies) - 1
            _draw_trophy(draw, cx, current_y, scale=drop_scale, glow=(glow if is_top else 0.0))

    # --- sub-label (only at peak) ---
    if frame >= CLIMB_END:
        prog = min(1.0, (frame - CLIMB_END) / 18)
        alpha = int(255 * prog)
        # Render through an RGBA layer so alpha actually applies
        sub_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sub_draw = ImageDraw.Draw(sub_layer)
        sub_draw.text(
            ((W - sub_draw.textlength("8 NATIONS · 22 TROPHIES", font=f_sublabel)) // 2, COL_SUBLABEL_Y - FS_BADGE // 2),
            "8 NATIONS · 22 TROPHIES",
            font=f_sublabel,
            fill=(*FG2, alpha),
        )
        img = Image.alpha_composite(img.convert("RGBA"), sub_layer).convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")

    # --- final tally row (numbers under codes) ---
    if frame >= CLIMB_END + 6:
        prog = min(1.0, (frame - CLIMB_END - 6) / 22)
        final_tally = tally()
        for i, code in enumerate(COLUMNS):
            cx = _col_center_x(i)
            n = final_tally[code]
            value_color = GOLD if i == 0 else WHITE
            # progressive wipe left-to-right
            if i / len(COLUMNS) > prog:
                continue
            _draw_text_centered(draw, str(n), f_tally_value, cy=COL_TALLY_Y, fill=value_color, cx=cx)

    # --- bottom band + CTA + source ---
    if frame >= PEAK_END - 6:
        prog = min(1.0, (frame - PEAK_END + 6) / 24)
        alpha = int(255 * prog)
        # band
        band_top_y = H - BAND_BOTTOM_H
        band_layer = Image.new("RGBA", (W, BAND_BOTTOM_H), (0, 0, 0, int(160 * prog)))
        img_rgba = img.convert("RGBA")
        img_rgba.paste(band_layer, (0, band_top_y), band_layer)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")
        _draw_text_centered(draw, "PICK YOUR CHAMPION", f_cta, cy=H - BAND_BOTTOM_H // 2, fill=WHITE)
        _draw_text_centered(draw, "Source: FIFA · 1930–2022", f_source, cy=H - BAND_BOTTOM_H - 26, fill=FG3)

    # --- watermark (always visible, bottom-left, in top band when CTA renders) ---
    draw.text((WATERMARK_PAD, WATERMARK_PAD), "pitch.predict", font=f_watermark, fill=FG3)

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
            if f % 60 == 0:
                print(f"  frame {f}/{TOTAL}", flush=True)
    finally:
        proc.stdin.close()
        proc.wait()
    return out_path


if __name__ == "__main__":
    out = ROOT / "output" / "wc_champions_pantheon_silent.mp4"
    render_to_mp4(out)
    print(f"Wrote {out} ({out.stat().st_size / 1024:.1f} KB)")
