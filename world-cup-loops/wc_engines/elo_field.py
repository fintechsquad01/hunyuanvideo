"""ELO Field engine — animated bar race for the 48 WC qualifiers.

V2: performance-optimized + brand-system-compliant.

Speed: pre-renders the static layout (background, rank numbers, team codes,
elo numbers, hook/CTA bands, watermark) ONCE, then per-frame only draws
the colored bars (rectangles, no Gaussian blur) at their current animated
width. ~50× faster than v1 which blurred 48 row shadows per frame.

Design tokens (per pitch.predict design system):
- Background: linear gradient #0d2818 → #08180e → #020a05
- Brand primary: #0f9d58 (pitch green)
- Brand yellow: #ffd400 (FIFA)
- Danger: #ff4d4d
- Overlay band: rgba(0, 0, 0, 0.60)
- Hook: Inter Bold or Anton, ALL CAPS, tracking -0.02em
- Numerics: Roboto Condensed Bold, tabular nums
- Display / winner: Anton
- Watermark: top-left, 40% opacity icon
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# Font lookup
_DESIGN_FONTS = (
    Path(__file__).resolve().parent.parent / "design" / "project" / "fonts"
)
_INTER_PATHS = (
    Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
    Path("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"),
)


def _font(family: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = []
    if family == "anton":
        candidates = [_DESIGN_FONTS / "Anton-Regular.ttf"]
    elif family == "bebas":
        candidates = [_DESIGN_FONTS / "BebasNeue-Regular.ttf"]
    elif family == "roboto_cond":
        candidates = [
            _DESIGN_FONTS / "RobotoCondensed-Bold.ttf",
            _DESIGN_FONTS / "RobotoCondensed.ttf",
        ]
    elif family == "inter_bold":
        candidates = [
            Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
            Path("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"),
        ]
    elif family == "inter_semi":
        candidates = [
            Path("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"),
            Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
        ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    # ultimate fallback
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
    )


def _hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _ease_out(t):
    return 1 - (1 - t) ** 3


@dataclass
class TeamRow:
    rank: int
    code: str
    name: str
    elo: int
    color: tuple
    highlight: str | None = None


class EloFieldEngine:
    def __init__(self, cfg, seed=11):
        self.w, self.h = cfg["resolution"]
        self.duration = cfg["duration"]
        self.fps = cfg["fps"]
        self.num_frames = self.duration * self.fps

        # Design tokens
        self.bg_top = _hex(cfg.get("background_top", "#0d2818"))
        self.bg_mid = _hex(cfg.get("background_mid", "#08180e"))
        self.bg_bot = _hex(cfg.get("background_bottom", "#020a05"))
        self.brand_green = _hex(cfg.get("brand_green", "#0f9d58"))
        self.brand_gold = _hex(cfg.get("brand_gold", "#ffd400"))
        self.danger = _hex(cfg.get("danger", "#ff4d4d"))
        self.fg_secondary = _hex(cfg.get("fg_secondary", "#8aa195"))

        # Layout (per design spec)
        self.band_h = int(self.h * 0.07)
        self.list_top = self.band_h + 40
        self.list_bottom = self.h - self.band_h - 30
        self.list_h = self.list_bottom - self.list_top

        # Teams
        self.teams: list[TeamRow] = []
        for i, t in enumerate(cfg["teams"]):
            self.teams.append(TeamRow(
                rank=i + 1,
                code=t["code"],
                name=t.get("name", t["code"]),
                elo=int(t["elo"]),
                color=_hex(t["color"]),
                highlight=t.get("highlight"),
            ))

        self.row_h = self.list_h / max(len(self.teams), 1)
        self.max_elo = max(t.elo for t in self.teams)
        self.min_elo = min(t.elo for t in self.teams)
        self.elo_range = self.max_elo - self.min_elo

        # Animation timing (seconds → frames)
        self.grow_end = int(self.fps * 2.2)
        self.spotlight_start = self.grow_end + 8
        self.spotlight_end = self.spotlight_start + int(self.fps * 6.5)
        self.hold_start = self.spotlight_end + 8

        # Fonts (per design spec)
        row_size = max(int(self.row_h * 0.46), 14)
        self.font_rank = _font("roboto_cond", max(int(self.row_h * 0.55), 16))
        self.font_code = _font("inter_bold", row_size)
        self.font_elo = _font("roboto_cond", row_size)
        self.font_hook = _font("anton", 64)
        self.font_cta = _font("anton", 52)
        self.font_brand = _font("inter_semi", 30)

        # Content — prefer engine_* fields (set when central overlay is disabled)
        overlay_cfg = cfg.get("overlay") or {}
        self.hook_text = cfg.get("engine_hook_text") or overlay_cfg.get("hook_text", "")
        self.cta_text = cfg.get("engine_cta_text") or overlay_cfg.get("cta_text", "")
        self.brand_mark = cfg.get("brand_mark", "pitch.predict")

        # Layout constants
        self.gutter = 16
        self.rank_w = 80
        self.code_w = 130
        self.elo_w = 100
        self.bar_x0 = self.rank_w + self.code_w + self.gutter
        self.bar_x1_max = self.w - self.elo_w - self.gutter - 30
        self.bar_max_width = self.bar_x1_max - self.bar_x0

        # Pre-render the static layout (everything that doesn't change)
        self._static = self._render_static_layout()

    # ---------- caching ----------

    def _render_background(self) -> Image.Image:
        bg = Image.new("RGB", (self.w, self.h), self.bg_top)
        px = bg.load()
        h = self.h
        for y in range(h):
            t = y / max(h - 1, 1)
            if t < 0.55:
                color = _lerp_color(self.bg_top, self.bg_mid, t / 0.55)
            else:
                color = _lerp_color(self.bg_mid, self.bg_bot, (t - 0.55) / 0.45)
            for x in range(self.w):
                px[x, y] = color
        return bg

    def _render_static_layout(self) -> Image.Image:
        """Pre-render everything that doesn't change per frame."""
        img = self._render_background().convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")

        # Subtle alternating row striping
        for idx in range(len(self.teams)):
            if idx % 2 == 1:
                y = self.list_top + idx * self.row_h
                draw.rectangle(
                    [20, int(y), self.w - 20, int(y + self.row_h)],
                    fill=(255, 255, 255, 10),
                )

        # Rank numbers, team codes, elo numbers
        for idx, team in enumerate(self.teams):
            y = self.list_top + idx * self.row_h
            y_center = y + self.row_h / 2

            # Rank
            rank_text = f"{team.rank:2d}"
            bbox = draw.textbbox((0, 0), rank_text, font=self.font_rank)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            rank_color = self.fg_secondary
            if team.highlight == "favorite":
                rank_color = self.brand_gold
            elif team.highlight == "underdog":
                rank_color = self.danger
            draw.text(
                (20 + (self.rank_w - tw) // 2, y_center - th / 2 - 3),
                rank_text,
                font=self.font_rank,
                fill=rank_color,
            )

            # Team code (placed where bar will START, so it sits inside the bar area)
            bbox = draw.textbbox((0, 0), team.code, font=self.font_code)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(
                (self.rank_w + 24, y_center - th / 2 - 2),
                team.code,
                font=self.font_code,
                fill="white",
                stroke_width=2,
                stroke_fill="black",
            )

            # Elo number (right)
            elo_text = f"{team.elo}"
            bbox = draw.textbbox((0, 0), elo_text, font=self.font_elo)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(
                (self.w - 30 - tw, y_center - th / 2 - 2),
                elo_text,
                font=self.font_elo,
                fill="white",
                stroke_width=2,
                stroke_fill="black",
            )

        # Hook band (top, ALL CAPS per spec)
        if self.hook_text:
            self._draw_band(img, self.hook_text.upper(), self.font_hook,
                            int(self.h * 0.018))

        # CTA band (bottom)
        if self.cta_text:
            self._draw_band(img, self.cta_text.upper(), self.font_cta,
                            int(self.h * 0.927))

        # Brand watermark (top-left). Spec calls for 40% on the ICON; for text
        # mark we boost to 65% so it reads through the brand identification at
        # 1080×1920 mobile view.
        wm_draw = ImageDraw.Draw(img, "RGBA")
        wm_x = 28
        wm_y = self.band_h + 30
        wm_draw.text(
            (wm_x, wm_y),
            self.brand_mark,
            font=self.font_brand,
            fill=(255, 255, 255, 165),
            stroke_width=2,
            stroke_fill=(0, 0, 0, 180),
        )

        return img

    def _draw_band(self, img, text, font, y_top):
        """Translucent black band with white text. ALL CAPS, tight tracking via spec."""
        draw = ImageDraw.Draw(img, "RGBA")
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad_x, pad_y = 36, 18
        x0 = (self.w - tw) // 2 - pad_x
        x1 = (self.w + tw) // 2 + pad_x
        y0 = y_top - pad_y
        y1 = y_top + th + pad_y
        draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 153))  # 60% black
        draw.text(
            ((self.w - tw) // 2, y_top),
            text,
            font=font,
            fill="white",
            stroke_width=3,
            stroke_fill="black",
        )

    # ---------- per-frame rendering ----------

    def frame(self, i: int) -> Image.Image:
        # Start from the cached static layout
        img = self._static.copy()
        draw = ImageDraw.Draw(img, "RGBA")

        # Determine which row (if any) is in the spotlight
        spotlight_idx = -1
        if self.spotlight_start <= i <= self.spotlight_end:
            t = (i - self.spotlight_start) / max(self.spotlight_end - self.spotlight_start, 1)
            spotlight_idx = int(t * len(self.teams))

        for idx, team in enumerate(self.teams):
            y = self.list_top + idx * self.row_h

            # Bar growth animation: rows stagger ~0.5 frame each
            if i >= self.grow_end:
                grow_t = 1.0
            else:
                row_delay = idx * 0.5
                local = max(0, i - row_delay)
                grow_t = _ease_out(min(local / max(self.grow_end - 1, 1), 1.0))

            # Bar width proportional to (elo - min_elo)/(max_elo - min_elo)
            prop = (team.elo - self.min_elo) / max(self.elo_range, 1)
            prop = 0.20 + prop * 0.80
            bar_w = self.bar_max_width * prop * grow_t

            # Color tweaks
            color = team.color
            if idx == spotlight_idx:
                color = tuple(min(255, int(c * 1.30 + 50)) for c in color)
            elif team.highlight == "favorite" and i >= self.hold_start - 30:
                color = tuple(min(255, int(c * 1.15 + 20)) for c in color)

            # Draw bar (rounded rect)
            top = y + 4
            bot = y + self.row_h - 4
            draw.rounded_rectangle(
                [self.bar_x0, top, self.bar_x0 + bar_w, bot],
                radius=6,
                fill=color,
            )

            # Highlight glow (no Gaussian — just outline + glow rect)
            do_glow = (
                idx == spotlight_idx
                or (team.highlight in ("favorite", "underdog") and i >= self.hold_start - 30)
            )
            if do_glow:
                glow_color = (255, 255, 255)
                if team.highlight == "favorite":
                    glow_color = self.brand_gold
                elif team.highlight == "underdog":
                    glow_color = self.danger
                # Triple outline at decreasing alpha for fake glow
                for offset, alpha in [(2, 220), (5, 110), (9, 55)]:
                    draw.rounded_rectangle(
                        [self.bar_x0 - offset, top - offset,
                         self.bar_x0 + bar_w + offset, bot + offset],
                        radius=6 + offset,
                        outline=glow_color + (alpha,),
                        width=2,
                    )

        return img

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
