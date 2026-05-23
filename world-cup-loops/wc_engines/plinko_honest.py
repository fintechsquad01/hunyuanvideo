"""Plinko Honest — vertical Plinko race with Elo-weighted marbles.

The sister mechanic to battle_royale_honest. 32 country marbles drop
through a Plinko peg-board; first to cross the finish line wins.

Per PIECE_LOCK.md:
- Marble size + mass + initial speed all proportional to real Elo
- Mass-weighted marble-marble collisions
- No rigging — whoever crosses first, wins
- Engine self-reports winner_code + winner_frame
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

_DESIGN_FONTS = (
    Path(__file__).resolve().parent.parent / "design" / "project" / "fonts"
)


def _font(family, size):
    candidates = []
    if family == "anton":
        candidates = [_DESIGN_FONTS / "Anton-Regular.ttf"]
    elif family == "roboto_cond":
        candidates = [_DESIGN_FONTS / "RobotoCondensed-Bold.ttf"]
    elif family == "inter_bold":
        candidates = [Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf")]
    elif family == "inter_semi":
        candidates = [Path("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"),
                      Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf")]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def _hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


@dataclass
class Marble:
    code: str
    color: tuple
    elo: int
    pos: np.ndarray
    vel: np.ndarray
    radius: float
    mass: float
    finished_frame: int | None = None


@dataclass
class Peg:
    pos: np.ndarray
    radius: float


class PlinkoHonestEngine:
    def __init__(self, cfg: dict, seed: int = 7):
        self.w, self.h = cfg["resolution"]
        self.duration = cfg["duration"]
        self.fps = cfg["fps"]
        self.num_frames = self.duration * self.fps
        self.dt = 1.0 / self.fps

        # Palette
        self.bg_top = _hex(cfg.get("bg_top", "#0d2818"))
        self.bg_mid = _hex(cfg.get("bg_mid", "#08180e"))
        self.bg_bot = _hex(cfg.get("bg_bot", "#020a05"))
        self.brand_gold = _hex(cfg.get("brand_gold", "#ffd400"))
        self.brand_green = _hex(cfg.get("brand_green", "#0f9d58"))

        # Plinko layout
        self.peg_rows = cfg.get("peg_rows", 18)
        self.peg_spacing = cfg.get("peg_spacing", 80)
        self.peg_radius = cfg.get("peg_radius", 7)
        self.gravity = cfg.get("gravity", 1400)
        self.bounce = cfg.get("bounce", 0.55)
        self.finish_y_pct = cfg.get("finish_y_pct", 0.94)
        self.start_y_pct = cfg.get("start_y_pct", 0.18)

        self.finish_y = int(self.h * self.finish_y_pct)
        self.start_y = int(self.h * self.start_y_pct)

        # Sizing config
        min_r = cfg.get("marble_min_radius", 17)
        max_r = cfg.get("marble_max_radius", 28)
        min_speed = cfg.get("marble_min_speed", 0)
        max_speed = cfg.get("marble_max_speed", 30)

        # Chrome
        self.hook_text = cfg.get("hook_text", "")
        self.cta_text = cfg.get("cta_text", "")
        self.brand_mark = cfg.get("brand_mark", "pitch.predict")
        self.round_chip = cfg.get("round_chip", "WC 2026 · R32 BRACKET")

        # Teams + elo
        teams = cfg["teams"]
        elos = [t["elo"] for t in teams]
        min_elo, max_elo = min(elos), max(elos)
        elo_range = max(max_elo - min_elo, 1)

        rng = random.Random(seed)
        np_rng = np.random.default_rng(seed)
        self.np_rng = np_rng  # store for use in step()

        n = len(teams)
        margin = max_r * 1.8
        positions_x = np.linspace(margin, self.w - margin, n)
        # Shuffle starting positions so favorites aren't all in same column
        idx_order = list(range(n))
        rng.shuffle(idx_order)

        self.marbles: list[Marble] = []
        for slot_i, t_i in enumerate(idx_order):
            t = teams[t_i]
            elo_t = (t["elo"] - min_elo) / elo_range
            radius = min_r + elo_t * (max_r - min_r)
            mass = radius ** 2
            speed = min_speed + elo_t * (max_speed - min_speed) + np_rng.uniform(-5, 5)
            v_angle = np_rng.uniform(-math.pi / 3, math.pi / 3) + math.pi / 2
            vel = np.array([math.cos(v_angle) * speed, math.sin(v_angle) * abs(speed)],
                           dtype=np.float64)
            jitter_x = np_rng.uniform(-8, 8)
            pos = np.array([positions_x[slot_i] + jitter_x, self.start_y + np_rng.uniform(-12, 0)],
                           dtype=np.float64)
            self.marbles.append(Marble(
                code=t["code"], color=_hex(t["color"]),
                elo=int(t["elo"]),
                pos=pos, vel=vel,
                radius=radius, mass=mass,
            ))

        # Pegs: offset grid (standard Plinko)
        self.pegs = self._build_pegs()

        # Track
        self.winner: Marble | None = None
        self.winner_frame: int | None = None
        self.finish_frames: list[int] = []  # frames at which marbles cross finish (in order)
        self.finish_order: list[str] = []

        self.bg_cache = self._render_background()

        self.font_code = _font("inter_bold", 14)
        self.font_counter = _font("roboto_cond", 56)
        self.font_counter_label = _font("inter_semi", 22)
        self.font_hook = _font("anton", 72)
        self.font_cta = _font("anton", 50)
        self.font_brand = _font("inter_semi", 28)
        self.font_chip = _font("roboto_cond", 22)
        self.font_payoff_main = _font("anton", 200)
        self.font_payoff_sub = _font("inter_bold", 40)
        self.font_payoff_eyebrow = _font("roboto_cond", 28)

    def _build_pegs(self):
        pegs = []
        top_y = int(self.h * 0.26)
        bottom_y = int(self.h * 0.90)
        rows = self.peg_rows
        row_step = (bottom_y - top_y) / max(rows - 1, 1)
        for row in range(rows):
            y = top_y + row * row_step
            offset = (self.peg_spacing / 2) if row % 2 == 1 else 0
            x = offset
            while x < self.w:
                if 30 < x < self.w - 30:
                    pegs.append(Peg(pos=np.array([x, y], dtype=np.float64),
                                    radius=self.peg_radius))
                x += self.peg_spacing
        return pegs

    def _render_background(self):
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

    def step(self, i: int):
        # Move marbles still in play
        for m in self.marbles:
            if m.finished_frame is not None:
                continue
            m.vel[1] += self.gravity * self.dt
            m.pos += m.vel * self.dt

            # Walls
            if m.pos[0] - m.radius < 0:
                m.pos[0] = m.radius
                m.vel[0] *= -self.bounce
            elif m.pos[0] + m.radius > self.w:
                m.pos[0] = self.w - m.radius
                m.vel[0] *= -self.bounce

            # Peg collisions
            for peg in self.pegs:
                delta = m.pos - peg.pos
                dist = float(np.linalg.norm(delta))
                min_dist = m.radius + peg.radius
                if dist < min_dist and dist > 1e-6:
                    normal = delta / dist
                    overlap = min_dist - dist
                    m.pos += normal * overlap
                    vn = float(np.dot(m.vel, normal))
                    if vn < 0:
                        m.vel -= (1 + self.bounce) * vn * normal
                        # Slight tangent kick for asymmetry
                        tangent = np.array([-normal[1], normal[0]])
                        m.vel += tangent * self.np_rng.uniform(-20, 20)

            # Finish line
            if m.pos[1] + m.radius >= self.finish_y and m.finished_frame is None:
                m.finished_frame = i
                self.finish_frames.append(i)
                self.finish_order.append(m.code)
                if self.winner is None:
                    self.winner = m
                    self.winner_frame = i

        # Marble-marble collisions (mass-weighted)
        active = [m for m in self.marbles if m.finished_frame is None]
        for a in range(len(active)):
            ma = active[a]
            for b in range(a + 1, len(active)):
                mb = active[b]
                delta = mb.pos - ma.pos
                dist = float(np.linalg.norm(delta))
                min_dist = ma.radius + mb.radius
                if dist < min_dist and dist > 1e-6:
                    normal = delta / dist
                    overlap = min_dist - dist
                    total_mass = ma.mass + mb.mass
                    ma.pos -= normal * overlap * (mb.mass / total_mass)
                    mb.pos += normal * overlap * (ma.mass / total_mass)
                    v1n = float(np.dot(ma.vel, normal))
                    v2n = float(np.dot(mb.vel, normal))
                    if v1n - v2n > 0:
                        continue
                    new_v1n = (v1n * (ma.mass - mb.mass) + 2 * mb.mass * v2n) / total_mass
                    new_v2n = (v2n * (mb.mass - ma.mass) + 2 * ma.mass * v1n) / total_mass
                    ma.vel += (new_v1n - v1n) * normal
                    mb.vel += (new_v2n - v2n) * normal

    # ----- drawing -----

    def _draw_banded(self, img, text, font, y_top, alpha=180):
        draw = ImageDraw.Draw(img, "RGBA")
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 32, 16
        x0 = (self.w - tw) // 2 - pad_x
        x1 = (self.w + tw) // 2 + pad_x
        y0 = y_top - pad_y
        y1 = y_top + th + pad_y
        draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, alpha))
        draw.text(((self.w - tw) // 2, y_top), text, font=font, fill="white",
                  stroke_width=3, stroke_fill="black")

    def _draw_watermark(self, img):
        draw = ImageDraw.Draw(img, "RGBA")
        draw.text((28, 28), self.brand_mark, font=self.font_brand,
                  fill=(255, 255, 255, 165), stroke_width=2, stroke_fill=(0, 0, 0, 180))

    def _draw_round_chip(self, img):
        draw = ImageDraw.Draw(img, "RGBA")
        text = self.round_chip
        bbox = draw.textbbox((0, 0), text, font=self.font_chip)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 14, 8
        x0 = self.w - tw - 28 - pad_x
        x1 = self.w - 28 + pad_x
        y0 = 28
        y1 = 28 + th + pad_y * 2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=999, fill=(*self.brand_green, 230))
        draw.text((x0 + pad_x, y0 + pad_y - 2), text, font=self.font_chip, fill="white")

    def _draw_counter(self, img, racing: int, total: int):
        draw = ImageDraw.Draw(img, "RGBA")
        text = f"{racing:02d}"
        label = f"OF {total} RACING"
        x = 60
        y = 130
        color = self.brand_gold if racing == 1 else (255, 255, 255)
        draw.text((x, y), text, font=self.font_counter, fill=color,
                  stroke_width=3, stroke_fill="black")
        draw.text((x + 4, y + 70), label, font=self.font_counter_label,
                  fill=(218, 230, 223, 200))

    def _draw_pegs(self, draw):
        for peg in self.pegs:
            x, y = peg.pos
            r = peg.radius
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(160, 165, 175))
            draw.ellipse([x - r * 0.5, y - r * 0.7, x + r * 0.2, y - r * 0.1],
                         fill=(220, 224, 230))

    def _draw_finish_line(self, draw):
        # White line + checkered
        y = self.finish_y
        draw.line([(0, y), (self.w, y)], fill=(255, 255, 255), width=3)
        for x in range(0, self.w, 50):
            checker_y = y + ((x // 50) % 2) * 14
            draw.rectangle([x, checker_y, x + 25, checker_y + 14], fill="white")

    def _draw_payoff(self, img, frame: int):
        if self.winner is None or self.winner_frame is None:
            return
        if frame < self.winner_frame:
            return
        fade = min((frame - self.winner_frame) / 20, 1.0)
        scrim = Image.new("RGBA", img.size, (0, 0, 0, int(210 * fade)))
        img.paste(scrim, (0, 0), scrim)

        draw = ImageDraw.Draw(img, "RGBA")
        eb = "PHYSICS PICKED"
        bbox = draw.textbbox((0, 0), eb, font=self.font_payoff_eyebrow)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        cy = self.h // 2
        draw.text(((self.w - tw) // 2, cy - 220), eb,
                  font=self.font_payoff_eyebrow, fill=(218, 230, 223, 220))

        text = self.winner.code
        bbox = draw.textbbox((0, 0), text, font=self.font_payoff_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((self.w - tw) // 2, cy - th // 2),
                  text, font=self.font_payoff_main,
                  fill=self.brand_gold, stroke_width=5, stroke_fill="black")

        sub = f"ELO {self.winner.elo}"
        bbox = draw.textbbox((0, 0), sub, font=self.font_payoff_sub)
        sw = bbox[2] - bbox[0]
        draw.text(((self.w - sw) // 2, cy + th // 2 + 30),
                  sub, font=self.font_payoff_sub,
                  fill="white", stroke_width=2, stroke_fill="black")

    def frame(self, i: int) -> Image.Image:
        img = self.bg_cache.copy()
        draw = ImageDraw.Draw(img, "RGBA")

        # Pegs first (under marbles)
        self._draw_pegs(draw)

        # Finish line
        self._draw_finish_line(draw)

        # Marble shadows
        for m in self.marbles:
            if m.finished_frame is not None:
                continue
            x, y = m.pos
            r = m.radius
            draw.ellipse([x - r * 0.9, y + r * 0.6, x + r * 0.9, y + r * 1.05],
                         fill=(0, 0, 0, 120))

        # Marbles
        for m in self.marbles:
            if m.finished_frame is not None and self.winner is m:
                # Winner marble stays glowing at finish line
                pass
            elif m.finished_frame is not None:
                continue  # other finished marbles disappear
            x, y = m.pos
            r = m.radius

            # Winner glow
            if self.winner is m and m.finished_frame is not None:
                for offset, alpha in [(10, 110), (5, 200)]:
                    draw.ellipse([x - r - offset, y - r - offset,
                                  x + r + offset, y + r + offset],
                                 outline=(*self.brand_gold, alpha), width=3)

            # Glossy
            color = m.color
            light = tuple(min(255, int(c * 1.5 + 60)) for c in color)
            dark = tuple(int(c * 0.55) for c in color)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=dark)
            for k in range(int(r), 0, -2):
                tt = 1 - (k / r)
                blend = _lerp_color(dark, color, tt)
                draw.ellipse([x - k, y - k, x + k, y + k], fill=blend)
            hl = r * 0.42
            draw.ellipse([x - hl - r * 0.22, y - hl - r * 0.22,
                          x + hl - r * 0.22, y + hl - r * 0.22],
                         fill=light)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=(255, 255, 255, 170), width=2)

            # Label
            label = m.code
            bbox = draw.textbbox((0, 0), label, font=self.font_code)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((x - tw / 2, y - th / 2 - 2),
                      label, font=self.font_code, fill="white",
                      stroke_width=2, stroke_fill="black")

        # Counter
        racing = sum(1 for m in self.marbles if m.finished_frame is None)
        total = len(self.marbles)
        self._draw_counter(img, racing, total)

        # Round chip + watermark
        self._draw_round_chip(img)
        self._draw_watermark(img)

        # Hook band fades by 2.7s
        if i < int(self.fps * 2.7):
            self._draw_banded(img, self.hook_text.upper(), self.font_hook,
                              int(self.h * 0.025))

        # CTA band always after intro
        if i >= int(self.fps * 0.5):
            self._draw_banded(img, self.cta_text.upper(), self.font_cta,
                              int(self.h * 0.94))

        self._draw_payoff(img, i)

        return img

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
            self.step(i)
