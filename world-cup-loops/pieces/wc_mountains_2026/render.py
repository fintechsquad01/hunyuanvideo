"""Render the 16-venues mountain range — fal backdrop + deterministic skyline chart."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib.chrome import (  # noqa: E402
    W, H, FPS, font, load_backdrop, draw_text_centered,
    draw_hook_band, draw_cta_band, draw_watermark, draw_source_line,
    BAND_TOP_H, BAND_BOTTOM_H, WHITE, FG2, FG3, FG_MUTE, GOLD, GREEN_BRIGHT,
    FS_HOOK_XL, FS_NUM, FS_BADGE, FS_FINE, ease_out,
)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import VENUES, COUNTRY_COLOR  # noqa: E402

TOTAL_S = 14.0
FPS_TOTAL = int(TOTAL_S * FPS)  # 420

# Beats
HOOK_END = 60      # 0:00–0:02
REVEAL_END = 300   # 0:02–0:10  (bars rise in sequence)
PEAK_END = 390     # 0:10–0:13  (Mexico City spotlight)
CTA_END = 420      # 0:13–0:14

# Chart area (lower band of frame, above CTA band)
CHART_TOP = 1080
CHART_BOTTOM = H - BAND_BOTTOM_H - 80
CHART_H = CHART_BOTTOM - CHART_TOP        # 706
N = len(VENUES)

# Column geometry
COL_MARGIN_X = 40
CHART_W = W - 2 * COL_MARGIN_X
COL_W = (CHART_W - (N - 1) * 6) // N      # ~58
COL_GAP = (CHART_W - N * COL_W) // (N - 1)

MAX_ELEV = max(v["elev_m"] for v in VENUES)


def _col_x(i: int) -> int:
    return COL_MARGIN_X + i * (COL_W + COL_GAP)


def _bar_height(elev_m: int) -> int:
    """Log-ish scaling so the smaller stadiums are still visible."""
    # Use square-root to soften the dynamic range (2 → ~1.4, 2240 → ~47)
    return int(CHART_H * (math.sqrt(elev_m) / math.sqrt(MAX_ELEV)) * 0.95) + 6


def _reveal_progress(frame: int, idx: int) -> float:
    """0..1 for bar `idx`. Bars stagger left→right across REVEAL_END."""
    if frame < HOOK_END:
        return 0.0
    if frame >= REVEAL_END:
        return 1.0
    span = REVEAL_END - HOOK_END
    bar_start = HOOK_END + int(idx * span * 0.62 / max(1, N - 1))
    bar_dur = 30
    if frame < bar_start:
        return 0.0
    return min(1.0, (frame - bar_start) / bar_dur)


def render_frame(frame: int, backdrop: Image.Image) -> Image.Image:
    img = backdrop.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Hook band
    draw_hook_band(draw, "MOUNTAINS OF 2026", alpha=255)

    # Year/sub-title under hook
    f_sub = font("inter_bold", FS_BADGE)
    draw_text_centered(draw, "16 STADIUMS · 3 COUNTRIES · 2,237 m DELTA",
                       f_sub, cy=BAND_TOP_H + 50, fill=FG2)

    # Chart baseline (horizon)
    base_y = CHART_BOTTOM
    draw.line([(COL_MARGIN_X, base_y), (W - COL_MARGIN_X, base_y)],
              fill=(255, 255, 255, 56), width=2)

    # Bars
    f_code = font("cond", 22)
    f_elev = font("cond", 20)
    for i, v in enumerate(VENUES):
        prog = ease_out(_reveal_progress(frame, i))
        if prog <= 0:
            continue
        x = _col_x(i)
        h = _bar_height(v["elev_m"])
        bar_h = int(h * prog)
        y_top = base_y - bar_h
        color = COUNTRY_COLOR[v["country"]]
        # Fill + soft outline
        draw.rectangle([x, y_top, x + COL_W, base_y], fill=(*color, 230))
        draw.rectangle([x, y_top, x + COL_W, base_y], outline=(255, 255, 255, 80), width=1)

        # Peak halo on Mexico City after PEAK_END begins
        if v["code"] == "MEX" and frame >= REVEAL_END:
            halo_intensity = 0.45 + 0.20 * math.sin((frame - REVEAL_END) * 0.18)
            halo_alpha = int(140 * halo_intensity)
            # Soft halo on top
            for r_out, a in [(30, halo_alpha // 3), (22, halo_alpha // 2), (12, halo_alpha)]:
                draw.ellipse(
                    [x + COL_W // 2 - r_out, y_top - r_out,
                     x + COL_W // 2 + r_out, y_top + r_out],
                    fill=(255, 212, 0, a),
                )

        # Code label below baseline (3-letter)
        if prog > 0.4:
            txt_alpha = int(255 * min(1.0, (prog - 0.4) / 0.4))
            code_color = (*WHITE, txt_alpha)
            draw.text((x + COL_W // 2 - 14, base_y + 8), v["code"],
                      font=f_code, fill=code_color)
            # Elevation under code, only for the tallest 5 to avoid clutter
            if v["elev_m"] >= 180:
                elev_str = f"{v['elev_m']:,}m"
                bbox = draw.textbbox((0, 0), elev_str, font=f_elev)
                tw = bbox[2] - bbox[0]
                draw.text((x + COL_W // 2 - tw // 2, base_y + 34),
                          elev_str, font=f_elev, fill=(*FG2, txt_alpha))

    # PEAK-only winner readout above Mexico bar
    if frame >= REVEAL_END:
        prog = min(1.0, (frame - REVEAL_END) / 24)
        alpha = int(255 * prog)
        mex_i = next(i for i, v in enumerate(VENUES) if v["code"] == "MEX")
        x_mex = _col_x(mex_i) + COL_W // 2
        y_mex = base_y - _bar_height(2240) - 26
        f_peak = font("cond", 28)
        f_peak_num = font("cond", 44)
        msg = "HIGHEST PEAK"
        bbox = draw.textbbox((0, 0), msg, font=f_peak)
        tw = bbox[2] - bbox[0]
        # Make sure label doesn't run off-screen
        x_label = max(WATERMARK_PAD := 20, min(W - tw - 20, x_mex - tw // 2))
        draw.text((x_label, y_mex - 50), msg, font=f_peak, fill=(*GOLD, alpha))
        num = "2,240 m"
        nbbox = draw.textbbox((0, 0), num, font=f_peak_num)
        nw = nbbox[2] - nbbox[0]
        x_num = max(20, min(W - nw - 20, x_mex - nw // 2))
        draw.text((x_num, y_mex - 20), num, font=f_peak_num, fill=(*GOLD, alpha))

    # CTA band (fade in last 1s)
    if frame >= PEAK_END - 10:
        prog = min(1.0, (frame - PEAK_END + 10) / 28)
        alpha = int(255 * prog)
        draw_cta_band(draw, "FIRST TRI-COUNTRY WORLD CUP", alpha=alpha,
                      cta_font="anton", cta_size=64)
        draw_source_line(draw, "Source: FIFA WC2026 venues · stadium-floor elevation",
                         alpha=int(200 * prog))

    draw_watermark(draw)
    return img.convert("RGB")


def render_to_mp4(out_path: Path, backdrop_path: Path | None = None) -> Path:
    out_path.parent.mkdir(exist_ok=True, parents=True)
    backdrop = load_backdrop(backdrop_path)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-preset", "medium", "-crf", "20",
        str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for f in range(FPS_TOTAL):
            img = render_frame(f, backdrop)
            proc.stdin.write(img.tobytes())
            if f % 60 == 0:
                print(f"  frame {f}/{FPS_TOTAL}", flush=True)
    finally:
        proc.stdin.close()
        proc.wait()
    return out_path


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "output" / "wc_mountains_2026_silent.mp4"
    render_to_mp4(out)
    print(f"Wrote {out}")
