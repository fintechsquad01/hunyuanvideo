"""Path Explainer — answers 'How far can [country] go in WC2026?'

A reveal-style data-driven piece. One country at a time. Hero card up top,
then 6 stage cards (R32 → R16 → QF → SF → Final → Champion) slide in one
by one, each with a probability bar that counts up from 0 to the simulated
value. Big payoff card at the end with the inverse-probability framing
('1 in 5 chance of winning').

No physics. Pure information design.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

_DESIGN_FONTS = (
    Path(__file__).resolve().parent.parent / "design" / "project" / "fonts"
)


def _font(family: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = []
    if family == "anton":
        candidates = [_DESIGN_FONTS / "Anton-Regular.ttf"]
    elif family == "bebas":
        candidates = [_DESIGN_FONTS / "BebasNeue-Regular.ttf"]
    elif family == "roboto_cond":
        candidates = [_DESIGN_FONTS / "RobotoCondensed-Bold.ttf",
                      _DESIGN_FONTS / "RobotoCondensed.ttf"]
    elif family == "inter_bold":
        candidates = [Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
                      Path("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf")]
    elif family == "inter_semi":
        candidates = [Path("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"),
                      Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf")]
    elif family == "inter_reg":
        candidates = [Path("/usr/share/fonts/opentype/inter/Inter-Regular.otf"),
                      Path("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf")]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def _hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def _ease_out_quart(t):
    return 1 - (1 - t) ** 4


# Stage definitions — order matters
STAGES = [
    ("R32", "ROUND OF 32"),
    ("R16", "ROUND OF 16"),
    ("QF",  "QUARTERFINALS"),
    ("SF",  "SEMIFINALS"),
    ("F",   "THE FINAL"),
    ("CHAMP", "WORLD CHAMPION"),
]


class PathExplainerEngine:
    def __init__(self, cfg: dict, seed: int = 0):
        self.w, self.h = cfg["resolution"]
        self.fps = cfg["fps"]
        self.duration = cfg["duration"]
        self.num_frames = int(self.duration * self.fps)

        # Brand palette
        self.bg_top = _hex(cfg.get("bg_top", "#0d2818"))
        self.bg_mid = _hex(cfg.get("bg_mid", "#08180e"))
        self.bg_bot = _hex(cfg.get("bg_bot", "#020a05"))
        self.brand_gold = _hex(cfg.get("brand_gold", "#ffd400"))
        self.brand_green = _hex(cfg.get("brand_green", "#0f9d58"))
        self.amber = _hex(cfg.get("amber", "#ffa726"))
        self.orange = _hex(cfg.get("orange", "#ff6b35"))
        self.red = _hex(cfg.get("red", "#ff4d4d"))

        # Country
        self.country = cfg["country"]   # code, name, color, world_rank, elo, confederation, manager
        # Probabilities — passed in same order as STAGES
        self.probs = [
            cfg["probabilities"]["r32"],
            cfg["probabilities"]["r16"],
            cfg["probabilities"]["qf"],
            cfg["probabilities"]["sf"],
            cfg["probabilities"]["final"],
            cfg["probabilities"]["champ"],
        ]

        # Chrome
        self.brand_mark = cfg.get("brand_mark", "pitch.predict")
        self.round_chip = cfg.get("round_chip", "WC 2026 · YOUR PATH")

        # Layout
        self.hero_top_y = 130
        self.hero_height = 360
        self.question_y = 540
        self.ladder_top_y = 660
        self.card_height = 122
        self.card_gap = 18
        self.card_x0 = 60
        self.card_x1 = self.w - 60

        # Timing (in frames)
        F = self.fps
        self.t_hero_start = 0
        self.t_hero_done = int(F * 0.9)
        self.t_question_start = int(F * 1.0)
        self.t_question_done = int(F * 1.6)
        # Each stage card animates over 1.4s; slight overlap between cards.
        self.t_stage_first = int(F * 1.7)
        self.t_stage_step = int(F * 1.1)   # next stage starts 1.1s after previous
        self.t_stage_anim = int(F * 1.3)   # each stage's full reveal (slide + count) duration
        # After all 6 stages done:
        self.t_all_done = self.t_stage_first + 5 * self.t_stage_step + self.t_stage_anim
        # Hold all stage cards visible so viewer can read the whole ladder
        self.t_hold_done = self.t_all_done + int(F * 2.2)
        self.t_payoff_in = self.t_hold_done
        self.t_payoff_done = self.t_payoff_in + int(F * 0.8)

        # Fonts
        self.f_brand = _font("inter_semi", 28)
        self.f_chip = _font("roboto_cond", 22)
        self.f_country_code = _font("anton", 180)
        self.f_country_name = _font("inter_bold", 42)
        self.f_country_meta = _font("inter_semi", 28)
        self.f_country_coach = _font("inter_reg", 22)
        self.f_question = _font("anton", 58)
        self.f_stage_name = _font("anton", 44)
        self.f_stage_pct = _font("anton", 72)
        self.f_stage_pct_small = _font("roboto_cond", 32)
        self.f_payoff_big = _font("anton", 180)
        self.f_payoff_label = _font("anton", 56)
        self.f_payoff_eyebrow = _font("inter_semi", 26)
        self.f_cta = _font("anton", 42)

        self.bg_cache = self._render_background()

    # ----- background -----

    def _render_background(self) -> Image.Image:
        bg = Image.new("RGB", (self.w, self.h), self.bg_top)
        px = bg.load()
        for y in range(self.h):
            t = y / max(self.h - 1, 1)
            if t < 0.55:
                color = _lerp_color(self.bg_top, self.bg_mid, t / 0.55)
            else:
                color = _lerp_color(self.bg_mid, self.bg_bot, (t - 0.55) / 0.45)
            for x in range(self.w):
                px[x, y] = color
        return bg

    # ----- helpers -----

    def _bar_color(self, p: float) -> tuple:
        if p >= 0.50:
            return self.brand_green
        if p >= 0.10:
            return self.amber
        if p >= 0.01:
            return self.orange
        return self.red

    def _stage_color(self, stage_idx: int, p: float) -> tuple:
        # Champion row is always gold
        if stage_idx == 5:
            return self.brand_gold
        return self._bar_color(p)

    def _fmt_pct(self, p: float) -> str:
        if p >= 0.10:
            return f"{p * 100:.1f}%"
        if p >= 0.001:
            return f"{p * 100:.2f}%"
        return f"{p * 100:.3f}%"

    def _fmt_one_in_n(self, p: float) -> str:
        if p <= 0:
            return "0"
        n = 1.0 / p
        if n < 100:
            return f"1 IN {n:.0f}"
        if n < 1000:
            return f"1 IN {round(n / 10) * 10:.0f}"
        return f"1 IN {round(n / 100) * 100:.0f}"

    def _draw_watermark(self, img):
        draw = ImageDraw.Draw(img, "RGBA")
        draw.text((28, 28), self.brand_mark, font=self.f_brand,
                  fill=(255, 255, 255, 175), stroke_width=2, stroke_fill=(0, 0, 0, 200))

    def _draw_round_chip(self, img):
        draw = ImageDraw.Draw(img, "RGBA")
        text = self.round_chip
        bbox = draw.textbbox((0, 0), text, font=self.f_chip)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 14, 8
        x0 = self.w - tw - 28 - pad_x
        x1 = self.w - 28 + pad_x
        y0 = 28
        y1 = 28 + th + pad_y * 2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=999,
                               fill=(*self.brand_green, 230))
        draw.text((x0 + pad_x, y0 + pad_y - 2), text, font=self.f_chip, fill="white")

    # ----- hero card -----

    def _draw_hero(self, img, frame: int):
        # Fade-up animation
        t = (frame - self.t_hero_start) / max(self.t_hero_done - self.t_hero_start, 1)
        t = max(0, min(1, t))
        alpha_mul = _ease_out_cubic(t)
        y_offset = (1 - alpha_mul) * 30  # slide up 30px

        draw = ImageDraw.Draw(img, "RGBA")
        country_color = _hex(self.country["color"])

        # Background card with country color stripe
        cy = self.hero_top_y + y_offset
        card_x0, card_x1 = 50, self.w - 50
        card_y0, card_y1 = cy, cy + self.hero_height
        # Subtle card bg
        draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=22,
                               fill=(0, 0, 0, int(120 * alpha_mul)))
        # Color stripe on left
        stripe_w = 18
        draw.rounded_rectangle([card_x0, card_y0, card_x0 + stripe_w + 22, card_y1],
                               radius=22,
                               fill=(*country_color, int(255 * alpha_mul)))
        draw.rectangle([card_x0 + stripe_w, card_y0,
                        card_x0 + stripe_w + 22, card_y1],
                       fill=(*country_color, int(255 * alpha_mul)))

        # Country code (huge)
        code = self.country["code"]
        bbox = draw.textbbox((0, 0), code, font=self.f_country_code)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        code_x = card_x0 + stripe_w + 70
        code_y = card_y0 + 30
        draw.text((code_x, code_y), code, font=self.f_country_code,
                  fill=(*country_color, int(255 * alpha_mul)),
                  stroke_width=3, stroke_fill=(0, 0, 0, int(255 * alpha_mul)))

        # Right column: name, rank, elo, manager
        right_x = code_x + tw + 36
        rx = right_x
        ry = code_y + 12

        name = self.country["name"].upper()
        draw.text((rx, ry), name, font=self.f_country_name,
                  fill=(255, 255, 255, int(255 * alpha_mul)),
                  stroke_width=2, stroke_fill=(0, 0, 0, int(200 * alpha_mul)))
        ry += 56

        meta = f"#{self.country['world_rank']} IN THE WORLD"
        draw.text((rx, ry), meta, font=self.f_country_meta,
                  fill=(218, 230, 223, int(230 * alpha_mul)))
        ry += 38

        elo = f"ELO {self.country['elo']}  ·  {self.country['confederation']}"
        draw.text((rx, ry), elo, font=self.f_country_meta,
                  fill=(218, 230, 223, int(220 * alpha_mul)))
        ry += 38

        coach = f"Coach: {self.country['manager']}"
        draw.text((rx, ry), coach, font=self.f_country_coach,
                  fill=(180, 200, 188, int(200 * alpha_mul)))

    # ----- question -----

    def _draw_question(self, img, frame: int):
        if frame < self.t_question_start:
            return
        t = (frame - self.t_question_start) / max(
            self.t_question_done - self.t_question_start, 1)
        t = max(0, min(1, t))
        alpha = int(255 * _ease_out_cubic(t))
        text = f"HOW FAR CAN {self.country['code']} GO?"
        draw = ImageDraw.Draw(img, "RGBA")
        bbox = draw.textbbox((0, 0), text, font=self.f_question)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 22, 10
        x_center = self.w // 2
        x0 = x_center - tw // 2 - pad_x
        x1 = x_center + tw // 2 + pad_x
        y0 = self.question_y
        y1 = y0 + th + pad_y * 2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=12,
                               fill=(0, 0, 0, min(alpha, 175)))
        draw.text((x_center - tw // 2, y0 + pad_y - 2), text,
                  font=self.f_question,
                  fill=(255, 255, 255, alpha),
                  stroke_width=3, stroke_fill=(0, 0, 0, alpha))

    # ----- stage cards -----

    def _draw_stage_card(self, img, frame: int, stage_idx: int):
        # When does THIS stage start animating?
        t_start = self.t_stage_first + stage_idx * self.t_stage_step
        if frame < t_start:
            return
        t_end = t_start + self.t_stage_anim
        # Two phases: slide-in (first 40%), then count-up (last 60%) overlap with next
        slide_dur = int(self.t_stage_anim * 0.45)
        count_dur = self.t_stage_anim - slide_dur

        slide_t = min(max((frame - t_start) / max(slide_dur, 1), 0), 1)
        count_t = min(max((frame - t_start - slide_dur) / max(count_dur, 1), 0), 1)
        slide_eased = _ease_out_cubic(slide_t)
        count_eased = _ease_out_quart(count_t)

        target_p = self.probs[stage_idx]
        current_p = target_p * count_eased

        # Card position
        card_y = self.ladder_top_y + stage_idx * (self.card_height + self.card_gap)
        # Slide in from right
        x_offset = (1 - slide_eased) * 80
        x0 = self.card_x0 + x_offset
        x1 = self.card_x1 + x_offset
        y0 = card_y
        y1 = y0 + self.card_height

        draw = ImageDraw.Draw(img, "RGBA")

        # Card bg (dark with alpha)
        card_alpha = int(180 * slide_eased)
        draw.rounded_rectangle([x0, y0, x1, y1], radius=18,
                               fill=(0, 0, 0, card_alpha),
                               outline=(255, 255, 255, int(50 * slide_eased)),
                               width=2)

        # Probability bar fill (background)
        bar_color = self._stage_color(stage_idx, target_p)
        # Bar extends from left to current_p of card width
        bar_max_w = (x1 - x0) - 8
        bar_w = bar_max_w * current_p
        bar_x0 = x0 + 4
        bar_y0 = y0 + 4
        bar_x1 = bar_x0 + bar_w
        bar_y1 = y1 - 4
        # Use a slight gradient: from solid color to brighter at the right end
        if bar_w > 8:
            # Draw bar with subtle inner glow
            draw.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1],
                                   radius=14, fill=(*bar_color, 200))

        # Stage name (left)
        stage_label = STAGES[stage_idx][1]
        text_x = x0 + 28
        text_y = y0 + (self.card_height - 50) // 2
        draw.text((text_x, text_y), stage_label, font=self.f_stage_name,
                  fill=(255, 255, 255, int(255 * slide_eased)),
                  stroke_width=3, stroke_fill=(0, 0, 0, int(220 * slide_eased)))

        # Probability number (right)
        if current_p > 0.0001 or count_t > 0.02:
            pct_str = self._fmt_pct(current_p)
        else:
            pct_str = "0.0%"
        bbox = draw.textbbox((0, 0), pct_str, font=self.f_stage_pct)
        ptw = bbox[2] - bbox[0]
        pth = bbox[3] - bbox[1]
        pct_x = x1 - ptw - 28
        pct_y = y0 + (self.card_height - 76) // 2
        # Champion-row gold text, else white
        pct_color = self.brand_gold if stage_idx == 5 else (255, 255, 255)
        draw.text((pct_x, pct_y), pct_str, font=self.f_stage_pct,
                  fill=(*pct_color, int(255 * slide_eased)),
                  stroke_width=4, stroke_fill=(0, 0, 0, int(240 * slide_eased)))

    def _draw_connectors(self, img, frame: int):
        # Small downward arrow between revealed cards
        draw = ImageDraw.Draw(img, "RGBA")
        for i in range(len(STAGES) - 1):
            t_start_next = self.t_stage_first + (i + 1) * self.t_stage_step
            if frame < t_start_next:
                continue
            t = min(max((frame - t_start_next) / max(self.fps * 0.25, 1), 0), 1)
            alpha = int(160 * t)
            cy = self.ladder_top_y + i * (self.card_height + self.card_gap) + self.card_height
            cx = self.w // 2
            gap = self.card_gap
            # Tiny chevron
            size = 8
            draw.polygon([(cx - size, cy + 2),
                          (cx + size, cy + 2),
                          (cx, cy + gap - 4)],
                         fill=(255, 255, 255, alpha))

    # ----- payoff -----

    def _draw_payoff(self, img, frame: int):
        if frame < self.t_payoff_in:
            return
        t = (frame - self.t_payoff_in) / max(
            self.t_payoff_done - self.t_payoff_in, 1)
        t = max(0, min(1, t))
        ease = _ease_out_cubic(t)
        alpha = int(252 * ease)

        scrim = Image.new("RGBA", img.size, (0, 0, 0, alpha))
        img.paste(scrim, (0, 0), scrim)

        draw = ImageDraw.Draw(img, "RGBA")
        cy = self.h // 2

        # Eyebrow
        eb = f"{self.country['code']} HAS A"
        bbox = draw.textbbox((0, 0), eb, font=self.f_payoff_eyebrow)
        tw = bbox[2] - bbox[0]
        draw.text(((self.w - tw) // 2, cy - 360), eb,
                  font=self.f_payoff_eyebrow,
                  fill=(218, 230, 223, int(230 * ease)))

        # The big "1 IN N" number
        big = self._fmt_one_in_n(self.probs[5])
        bbox = draw.textbbox((0, 0), big, font=self.f_payoff_big)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((self.w - tw) // 2, cy - 240),
                  big, font=self.f_payoff_big,
                  fill=(*self.brand_gold, int(255 * ease)),
                  stroke_width=6, stroke_fill=(0, 0, 0, int(255 * ease)))

        # Sub label
        sub = "CHANCE OF WINNING"
        bbox = draw.textbbox((0, 0), sub, font=self.f_payoff_label)
        sw = bbox[2] - bbox[0]
        draw.text(((self.w - sw) // 2, cy - 240 + th + 8),
                  sub, font=self.f_payoff_label,
                  fill=(255, 255, 255, int(255 * ease)),
                  stroke_width=3, stroke_fill=(0, 0, 0, int(255 * ease)))

        sub2 = "THE 2026 WORLD CUP"
        bbox = draw.textbbox((0, 0), sub2, font=self.f_payoff_label)
        sw = bbox[2] - bbox[0]
        draw.text(((self.w - sw) // 2, cy - 240 + th + 8 + 70),
                  sub2, font=self.f_payoff_label,
                  fill=(255, 255, 255, int(255 * ease)),
                  stroke_width=3, stroke_fill=(0, 0, 0, int(255 * ease)))

        # Precise % below
        precise = f"({self._fmt_pct(self.probs[5])} per simulation · n=10,000)"
        bbox = draw.textbbox((0, 0), precise, font=self.f_payoff_eyebrow)
        sw = bbox[2] - bbox[0]
        draw.text(((self.w - sw) // 2, cy + 80),
                  precise, font=self.f_payoff_eyebrow,
                  fill=(180, 200, 188, int(220 * ease)))

        # CTA
        cta = "WHAT'S YOUR COUNTRY'S CHANCE?"
        bbox = draw.textbbox((0, 0), cta, font=self.f_cta)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]
        pad_x, pad_y = 26, 14
        y_cta = cy + 180
        draw.rounded_rectangle(
            [(self.w - sw) // 2 - pad_x, y_cta - pad_y,
             (self.w + sw) // 2 + pad_x, y_cta + sh + pad_y],
            radius=14, fill=(*self.brand_gold, int(230 * ease)))
        draw.text(((self.w - sw) // 2, y_cta), cta, font=self.f_cta,
                  fill=(0, 0, 0, int(255 * ease)))

    # ----- frame -----

    def frame(self, i: int) -> Image.Image:
        img = self.bg_cache.copy()

        # Hero (always drawn after start)
        self._draw_hero(img, i)
        # Question
        self._draw_question(img, i)
        # Stage cards
        for s in range(len(STAGES)):
            self._draw_stage_card(img, i, s)
        # Connectors
        self._draw_connectors(img, i)
        # Chrome
        self._draw_watermark(img)
        self._draw_round_chip(img)
        # Payoff overlay
        self._draw_payoff(img, i)
        return img

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
