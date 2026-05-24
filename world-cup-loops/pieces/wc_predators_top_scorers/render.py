"""Render Predators of the Goal — fal mood + deterministic leaderboard."""

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
    BAND_TOP_H, BAND_BOTTOM_H, WHITE, FG2, FG3, FG_MUTE, GOLD, ease_out,
)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import SCORERS, COUNTRY_ACCENT  # noqa: E402

TOTAL_S = 15.0
FPS_TOTAL = int(TOTAL_S * FPS)

# Beats: rows reveal bottom-to-top (rank 6 first, rank 1 last)
HOOK_END = 60       # 0:00–0:02  hook + mood
REVEAL_START = 90   # 0:03
REVEAL_END = 360    # 0:12  (6 rows over 9s = ~45 frames/row)
HALO_END = 420      # 0:14
CTA_END = 450       # 0:15

# Layout: leaderboard occupies lower half of frame
LB_TOP = 1000
LB_BOTTOM = H - BAND_BOTTOM_H - 100
ROW_GAP = 14
N_ROWS = len(SCORERS)
ROW_H = (LB_BOTTOM - LB_TOP - (N_ROWS - 1) * ROW_GAP) // N_ROWS

LB_X0 = 40
LB_X1 = W - 40


def _reveal_progress(frame: int, row_idx_from_bottom: int) -> float:
    """row_idx_from_bottom: 0 = rank #6 (appears first), 5 = rank #1 (last + halo)."""
    if frame < REVEAL_START:
        return 0.0
    span = REVEAL_END - REVEAL_START
    row_start = REVEAL_START + int(row_idx_from_bottom * span / N_ROWS)
    row_dur = 36
    if frame < row_start:
        return 0.0
    return min(1.0, (frame - row_start) / row_dur)


def _draw_row(draw: ImageDraw.ImageDraw, scorer: dict, y_top: int, alpha_f: float) -> None:
    a = int(255 * alpha_f)
    accent = COUNTRY_ACCENT[scorer["country"]]
    # Row background — translucent dark with accent left bar
    draw.rectangle([LB_X0, y_top, LB_X1, y_top + ROW_H],
                   fill=(0, 0, 0, int(170 * alpha_f)))
    draw.rectangle([LB_X0, y_top, LB_X0 + 8, y_top + ROW_H],
                   fill=(*accent, a))

    f_rank = font("anton", 84)
    f_name = font("inter_bold", 38)
    f_meta = font("inter_med", 22)
    f_goals = font("anton", 96)
    f_goals_label = font("cond", 22)

    # Rank big number on left
    rank_str = str(scorer["rank"])
    draw.text((LB_X0 + 32, y_top + (ROW_H - 84) // 2 - 4),
              rank_str, font=f_rank, fill=(*FG2, a))

    # Player name + meta
    name_x = LB_X0 + 140
    draw.text((name_x, y_top + 14), scorer["name"], font=f_name, fill=(*WHITE, a))
    meta = f"{scorer['country']}  ·  {scorer['wcs']}"
    draw.text((name_x, y_top + 60), meta, font=f_meta, fill=(*FG3, a))

    # Goals on the right
    goals_str = str(scorer["goals"])
    g_box = draw.textbbox((0, 0), goals_str, font=f_goals)
    g_w = g_box[2] - g_box[0]
    g_x = LB_X1 - 32 - g_w
    g_y = y_top + (ROW_H - 96) // 2 - 4
    draw.text((g_x, g_y), goals_str, font=f_goals, fill=(*WHITE, a))
    # "GOALS" label under the number
    lbl_w = draw.textlength("GOALS", font=f_goals_label)
    draw.text((g_x + (g_w - lbl_w) // 2, g_y + 100),
              "GOALS", font=f_goals_label, fill=(*FG3, a))


def render_frame(frame: int, backdrop: Image.Image) -> Image.Image:
    img = backdrop.copy().convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Hook + sub
    draw_hook_band(draw, "PREDATORS OF THE GOAL", alpha=255)
    f_sub = font("inter_bold", 28)
    draw_text_centered(draw, "ALL-TIME WC TOP SCORERS · THROUGH 2022",
                       f_sub, cy=BAND_TOP_H + 50, fill=FG2)

    # Leaderboard rows (rank 6 at bottom of board, rank 1 at top)
    for ri, scorer in enumerate(SCORERS):
        row_idx_from_bottom = (N_ROWS - 1) - ri  # rank 1 is rendered last
        y_top = LB_TOP + ri * (ROW_H + ROW_GAP)
        prog = _reveal_progress(frame, row_idx_from_bottom)
        if prog <= 0:
            continue
        # Slide-up animation: y starts +40px and eases up
        offset = int((1 - ease_out(prog)) * 40)
        _draw_row(draw, scorer, y_top + offset, alpha_f=prog)

    # Halo + gold on rank #1 after reveal completes
    if frame >= REVEAL_END:
        prog = min(1.0, (frame - REVEAL_END) / 24)
        a = int(255 * prog)
        y_top = LB_TOP + 0  # rank 1 is row index 0
        intensity = 0.55 + 0.20 * math.sin((frame - REVEAL_END) * 0.18)
        # Sustained gold halo on the row
        draw.rectangle(
            [LB_X0 - 6, y_top - 6, LB_X1 + 6, y_top + ROW_H + 6],
            outline=(255, 212, 0, int(160 * intensity * prog)), width=4,
        )
        # Repaint rank #1 number in gold
        f_rank = font("anton", 84)
        draw.text((LB_X0 + 32, y_top + (ROW_H - 84) // 2 - 4),
                  "1", font=f_rank, fill=(*GOLD, a))

    # CTA
    if frame >= HALO_END - 10:
        prog = min(1.0, (frame - HALO_END + 10) / 28)
        alpha = int(255 * prog)
        draw_cta_band(draw, "WHO'S YOUR GOAT?", alpha=alpha, cta_font="anton", cta_size=76)
        draw_source_line(draw, "Source: FIFA · official WC tournament records",
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
    out = Path(__file__).resolve().parents[2] / "output" / "wc_predators_top_scorers_silent.mp4"
    render_to_mp4(out)
    print(f"Wrote {out}")
