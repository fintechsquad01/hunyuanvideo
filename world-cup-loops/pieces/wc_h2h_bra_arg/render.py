"""Render the BRA vs ARG H2H piece — fal backdrop + counters + reveal."""

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
    BAND_TOP_H, BAND_BOTTOM_H, WHITE, FG2, FG3, GOLD, RED, ease_out, ease_in_out,
)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import MEETINGS, BRA_WINS, ARG_WINS, DRAWS, LEADER, LEAD  # noqa: E402

TOTAL_S = 14.0
FPS_TOTAL = int(TOTAL_S * FPS)

# Beats
HOOK_END = 60      # 0:00–0:02: hook + atmosphere
COUNTER_START = 75 # 0:02.5
COUNTER_END = 300  # 0:10  (counters animate)
LEAD_HALO_END = 390  # 0:13  (winner halo)
CTA_END = 420      # 0:14

# Color accents (flat brand)
BRA_ACCENT = (253, 198, 17)   # yellow (brand-safe — not a flag image)
ARG_ACCENT = (108, 188, 222)  # light blue
DRAW_ACCENT = (220, 220, 220)


def _counter_value(target: int, frame: int) -> int:
    if frame < COUNTER_START:
        return 0
    if frame >= COUNTER_END:
        return target
    t = (frame - COUNTER_START) / (COUNTER_END - COUNTER_START)
    return int(target * ease_out(t))


def render_frame(frame: int, backdrop: Image.Image) -> Image.Image:
    img = backdrop.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Hook band: BRAZIL vs ARGENTINA
    draw_hook_band(draw, "BRAZIL vs ARGENTINA", alpha=255)
    f_subhook = font("inter_bold", 28)
    draw_text_centered(draw, "FOOTBALL'S OLDEST WAR · ALL-TIME H2H",
                       f_subhook, cy=BAND_TOP_H + 50, fill=FG2)

    # Side labels + counters
    f_big = font("anton", 200)
    f_label = font("cond", 44)
    f_subnum = font("cond", 30)

    # Left column (BRA) center x, right column (ARG) center x
    cx_l, cx_r = 280, W - 280
    counter_cy = 1080
    label_cy = counter_cy - 200

    # Side labels
    draw.text((cx_l - 50, label_cy - 30), "BRA", font=f_label, fill=BRA_ACCENT)
    draw.text((cx_r - 50, label_cy - 30), "ARG", font=f_label, fill=ARG_ACCENT)

    # Big animated counters
    bra_val = _counter_value(BRA_WINS, frame)
    arg_val = _counter_value(ARG_WINS, frame)
    bra_str = str(bra_val)
    arg_str = str(arg_val)
    b_box = draw.textbbox((0, 0), bra_str, font=f_big)
    a_box = draw.textbbox((0, 0), arg_str, font=f_big)
    draw.text((cx_l - (b_box[2] - b_box[0]) // 2, counter_cy - (b_box[3] - b_box[1]) // 2 - b_box[1]),
              bra_str, font=f_big, fill=(*WHITE, 255))
    draw.text((cx_r - (a_box[2] - a_box[0]) // 2, counter_cy - (a_box[3] - a_box[1]) // 2 - a_box[1]),
              arg_str, font=f_big, fill=(*WHITE, 255))

    # "WINS" sub-label below each counter
    draw_text_centered(draw, "WINS", f_subnum, cy=counter_cy + 130, fill=FG2, cx=cx_l)
    draw_text_centered(draw, "WINS", f_subnum, cy=counter_cy + 130, fill=FG2, cx=cx_r)

    # Center "DRAWS" pill counter
    draws_val = _counter_value(DRAWS, frame)
    f_draw_num = font("anton", 110)
    draw_text_centered(draw, str(draws_val), f_draw_num, cy=counter_cy + 30, fill=FG2)
    draw_text_centered(draw, "DRAWS", f_subnum, cy=counter_cy + 130, fill=FG3)

    # Total meetings ticker (top, under hook)
    total_str = f"{_counter_value(MEETINGS, frame)} MEETINGS"
    f_total = font("cond", 42)
    draw_text_centered(draw, total_str, f_total, cy=BAND_TOP_H + 110, fill=WHITE)

    # Lead readout when counters lock
    if frame >= COUNTER_END:
        prog = min(1.0, (frame - COUNTER_END) / 24)
        alpha = int(255 * prog)
        # Halo behind the leader's counter
        if LEADER == "BRA":
            lx = cx_l
        else:
            lx = cx_r
        halo_intensity = 0.5 + 0.25 * math.sin((frame - COUNTER_END) * 0.18)
        for r_out, a_mul in [(180, 0.18), (130, 0.32), (90, 0.55), (60, 0.85)]:
            draw.ellipse(
                [lx - r_out, counter_cy - r_out, lx + r_out, counter_cy + r_out],
                fill=(255, 212, 0, int(80 * halo_intensity * a_mul * prog)),
            )
        # Re-draw the leader's number ON TOP of halo, in gold
        lead_str = str(BRA_WINS if LEADER == "BRA" else ARG_WINS)
        lbox = draw.textbbox((0, 0), lead_str, font=f_big)
        draw.text(
            (lx - (lbox[2] - lbox[0]) // 2,
             counter_cy - (lbox[3] - lbox[1]) // 2 - lbox[1]),
            lead_str, font=f_big, fill=(*GOLD, alpha),
        )

        # "+7" lead pill below center
        lead_label = f"+{LEAD}"
        f_lead = font("anton", 84)
        draw_text_centered(draw, lead_label, f_lead, cy=1380, fill=(*GOLD, alpha))
        draw_text_centered(draw, "BRAZIL LEADS", font("inter_bold", 32),
                           cy=1450, fill=(*WHITE, alpha))

    # CTA band
    if frame >= LEAD_HALO_END - 10:
        prog = min(1.0, (frame - LEAD_HALO_END + 10) / 28)
        alpha = int(255 * prog)
        draw_cta_band(draw, "WHO WINS NEXT?", alpha=alpha, cta_font="anton", cta_size=76)
        draw_source_line(draw, "Source: Elo Football · all FIFA-recognized meetings",
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
    out = Path(__file__).resolve().parents[2] / "output" / "wc_h2h_bra_arg_silent.mp4"
    render_to_mp4(out)
    print(f"Wrote {out}")
