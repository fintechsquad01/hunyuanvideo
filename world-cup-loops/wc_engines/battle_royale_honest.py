"""Battle Royale — HONEST version (per PIECE_LOCK.md).

48 country marbles in a shrinking arena. Marble size, mass, and initial
velocity are all proportional to real Elo rating. Eliminations happen
ONLY when a marble is pushed outside the shrinking safe zone by physics
— not by a predetermined schedule. The winner is whoever the physics
actually leaves standing.

Differences from the original rigged battle_royale.py:
- No `winner_code` config. No pre-scheduled elimination order.
- Marble radius = lerp from min_radius to max_radius proportional to Elo
- Marble mass = radius² (used in collision exchange — bigger marbles
  knock smaller ones around)
- Initial velocity magnitude proportional to Elo (favorites are punchier)
- Elimination is purely physics-driven: if a marble's center exits the
  shrinking arena radius for >12 frames, it's eliminated
- Engine self-reports the elimination frames (for audio sync) and the
  winner (for caption / payoff overlay)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
    eliminated_frame: int | None = None
    death_pos: np.ndarray | None = None
    outside_frames: int = 0  # how many consecutive frames the marble has been outside the safe zone


class BattleRoyaleHonestEngine:
    def __init__(self, cfg: dict, seed: int = 42):
        self.w, self.h = cfg["resolution"]
        self.duration = cfg["duration"]
        self.fps = cfg["fps"]
        self.num_frames = self.duration * self.fps
        self.dt = 1.0 / self.fps

        # Brand palette
        self.bg_top = _hex(cfg.get("bg_top", "#0d2818"))
        self.bg_mid = _hex(cfg.get("bg_mid", "#08180e"))
        self.bg_bot = _hex(cfg.get("bg_bot", "#020a05"))
        self.brand_gold = _hex(cfg.get("brand_gold", "#ffd400"))
        self.danger = _hex(cfg.get("danger", "#ff4d4d"))
        self.brand_green = _hex(cfg.get("brand_green", "#0f9d58"))

        # Arena
        ax = cfg.get("arena_cx", self.w // 2)
        ay = cfg.get("arena_cy", int(self.h * 0.52))
        self.center = np.array([ax, ay], dtype=np.float64)
        self.arena_r_start = cfg.get("arena_r_start", 470)
        self.arena_r_end = cfg.get("arena_r_end", 80)

        # Chrome content
        self.hook_text = cfg.get("hook_text", "")
        self.cta_text = cfg.get("cta_text", "")
        self.brand_mark = cfg.get("brand_mark", "pitch.predict")
        self.round_chip = cfg.get("round_chip", "WC 2026 · BATTLE OF THE 48")

        # Marble sizing config
        min_r = cfg.get("marble_min_radius", 16)
        max_r = cfg.get("marble_max_radius", 32)
        min_speed = cfg.get("marble_min_speed", 110)
        max_speed = cfg.get("marble_max_speed", 220)

        # Teams + elo
        teams = cfg["teams"]
        elos = [t["elo"] for t in teams]
        min_elo, max_elo = min(elos), max(elos)
        elo_range = max(max_elo - min_elo, 1)

        rng = random.Random(seed)
        np_rng = np.random.default_rng(seed)

        self.marbles: list[Marble] = []
        n = len(teams)
        spawn_r = self.arena_r_start * 0.70

        # Pre-distribute on a jittered ring
        for i, t in enumerate(teams):
            elo_t = (t["elo"] - min_elo) / elo_range
            radius = min_r + elo_t * (max_r - min_r)
            mass = radius ** 2          # 2D mass = area-proportional
            speed = min_speed + elo_t * (max_speed - min_speed)
            speed *= np_rng.uniform(0.85, 1.15)   # ±15% jitter

            angle = (i / n) * 2 * math.pi + np_rng.uniform(-0.06, 0.06)
            r_init = spawn_r * (0.35 + np_rng.uniform(0, 0.55))
            pos = self.center + np.array([
                math.cos(angle) * r_init,
                math.sin(angle) * r_init,
            ])
            v_angle = np_rng.uniform(0, 2 * math.pi)
            vel = np.array([math.cos(v_angle) * speed, math.sin(v_angle) * speed],
                           dtype=np.float64)

            self.marbles.append(Marble(
                code=t["code"], color=_hex(t["color"]),
                elo=int(t["elo"]),
                pos=pos, vel=vel,
                radius=radius, mass=mass,
            ))

        # Tracking
        self.elimination_frames: list[int] = []  # in order of elimination
        self.elimination_order: list[str] = []   # team codes in order of elimination
        self.winner: Marble | None = None
        self.winner_frame: int | None = None

        # Cache
        self.bg_cache = self._render_background()

        # Fonts
        self.font_code = _font("inter_bold", 15)
        self.font_counter = _font("roboto_cond", 56)
        self.font_counter_label = _font("inter_semi", 22)
        self.font_hook = _font("anton", 72)
        self.font_cta = _font("anton", 50)
        self.font_brand = _font("inter_semi", 28)
        self.font_chip = _font("roboto_cond", 22)
        self.font_payoff_main = _font("anton", 200)
        self.font_payoff_sub = _font("inter_bold", 40)
        self.font_payoff_eyebrow = _font("roboto_cond", 28)

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

    # ----- physics -----

    def _arena_radius(self, i: int) -> float:
        # Hold full size during intro, then shrink to ~80% by 75% of duration,
        # then aggressively to arena_r_end by the end.
        intro_frames = int(self.fps * 1.5)
        if i < intro_frames:
            return self.arena_r_start
        t = (i - intro_frames) / max(self.num_frames - intro_frames - 1, 1)
        if t < 0.75:
            eased = (t / 0.75) ** 1.2 * 0.75
        else:
            local = (t - 0.75) / 0.25
            eased = 0.75 + local * 0.25
        return self.arena_r_start - (self.arena_r_start - self.arena_r_end) * eased

    def step(self, i: int):
        arena_r = self._arena_radius(i)

        # Move alive marbles
        for m in self.marbles:
            if m.eliminated_frame is not None:
                continue
            m.pos += m.vel * self.dt

        # Marble-marble collisions (mass-weighted velocity exchange)
        alive = [m for m in self.marbles if m.eliminated_frame is None]
        for a in range(len(alive)):
            ma = alive[a]
            for b in range(a + 1, len(alive)):
                mb = alive[b]
                delta = mb.pos - ma.pos
                dist = float(np.linalg.norm(delta))
                min_dist = ma.radius + mb.radius
                if dist < min_dist and dist > 1e-6:
                    normal = delta / dist
                    overlap = min_dist - dist
                    # Position correction proportional to mass
                    total_mass = ma.mass + mb.mass
                    ma.pos -= normal * overlap * (mb.mass / total_mass)
                    mb.pos += normal * overlap * (ma.mass / total_mass)
                    # Velocity exchange (1D elastic collision along normal)
                    v1n = float(np.dot(ma.vel, normal))
                    v2n = float(np.dot(mb.vel, normal))
                    if v1n - v2n > 0:  # they're moving apart already
                        continue
                    new_v1n = (v1n * (ma.mass - mb.mass) + 2 * mb.mass * v2n) / total_mass
                    new_v2n = (v2n * (mb.mass - ma.mass) + 2 * ma.mass * v1n) / total_mass
                    ma.vel += (new_v1n - v1n) * normal
                    mb.vel += (new_v2n - v2n) * normal

        # Check arena boundary — eliminate if outside for too long
        for m in alive:
            offset = m.pos - self.center
            dist = float(np.linalg.norm(offset))
            if dist > arena_r:
                m.outside_frames += 1
                # Soft push back if just slightly out — gives a brief grace
                if m.outside_frames < 6:
                    # Bounce-back impulse toward center
                    normal = offset / max(dist, 1e-6)
                    vn = float(np.dot(m.vel, normal))
                    if vn > 0:
                        m.vel -= 1.4 * vn * normal
                else:
                    # Eliminated — outside the safe zone too long
                    m.eliminated_frame = i
                    m.death_pos = m.pos.copy()
                    self.elimination_frames.append(i)
                    self.elimination_order.append(m.code)
            else:
                m.outside_frames = 0

        # Detect winner once only 1 marble remains
        still_alive = [m for m in self.marbles if m.eliminated_frame is None]
        if self.winner is None and len(still_alive) == 1:
            self.winner = still_alive[0]
            self.winner_frame = i

    # ----- chrome drawing helpers -----

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

    def _draw_counter(self, img, alive_count, total):
        draw = ImageDraw.Draw(img, "RGBA")
        text = f"{alive_count:02d}"
        label = f"OF {total} ALIVE"
        x = 60
        y = 130
        color = self.brand_gold if alive_count == 1 else (255, 255, 255)
        draw.text((x, y), text, font=self.font_counter, fill=color,
                  stroke_width=3, stroke_fill="black")
        draw.text((x + 4, y + 70), label, font=self.font_counter_label,
                  fill=(218, 230, 223, 200))

    def _draw_payoff(self, img, frame: int):
        if self.winner is None or self.winner_frame is None:
            return
        if frame < self.winner_frame:
            return
        fade = min((frame - self.winner_frame) / 20, 1.0)
        scrim = Image.new("RGBA", img.size, (0, 0, 0, int(210 * fade)))
        img.paste(scrim, (0, 0), scrim)

        draw = ImageDraw.Draw(img, "RGBA")

        # Eyebrow
        eb = "PHYSICS PICKED"
        bbox = draw.textbbox((0, 0), eb, font=self.font_payoff_eyebrow)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        cy = self.h // 2
        draw.text(((self.w - tw) // 2, cy - 220), eb,
                  font=self.font_payoff_eyebrow,
                  fill=(218, 230, 223, 220))

        # Winner code (giant)
        text = self.winner.code
        bbox = draw.textbbox((0, 0), text, font=self.font_payoff_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((self.w - tw) // 2, cy - th // 2),
                  text, font=self.font_payoff_main,
                  fill=self.brand_gold,
                  stroke_width=5, stroke_fill="black")

        # Elo subtitle
        sub = f"ELO {self.winner.elo}"
        bbox = draw.textbbox((0, 0), sub, font=self.font_payoff_sub)
        sw = bbox[2] - bbox[0]
        draw.text(((self.w - sw) // 2, cy + th // 2 + 30),
                  sub, font=self.font_payoff_sub,
                  fill="white", stroke_width=2, stroke_fill="black")

    # ----- per-frame render -----

    def frame(self, i: int) -> Image.Image:
        img = self.bg_cache.copy()
        draw = ImageDraw.Draw(img, "RGBA")

        # Arena visuals
        arena_r = self._arena_radius(i)
        cx, cy = int(self.center[0]), int(self.center[1])
        # Outer fixed arena (faint)
        draw.ellipse([cx - self.arena_r_start, cy - self.arena_r_start,
                      cx + self.arena_r_start, cy + self.arena_r_start],
                     outline=(255, 255, 255, 22), width=2)
        # Active danger ring
        for offset, alpha in [(0, 200), (5, 100), (12, 50)]:
            draw.ellipse([cx - arena_r - offset, cy - arena_r - offset,
                          cx + arena_r + offset, cy + arena_r + offset],
                         outline=(*self.danger, alpha), width=2)

        # Marble shadows (alive only)
        for m in self.marbles:
            if m.eliminated_frame is not None:
                continue
            x, y = m.pos
            r = m.radius
            draw.ellipse([x - r * 0.95, y + r * 0.55, x + r * 0.95, y + r * 1.05],
                         fill=(0, 0, 0, 130))

        # Ghosts of eliminated marbles (last 18 frames)
        for m in self.marbles:
            if m.eliminated_frame is None:
                continue
            age = i - m.eliminated_frame
            if age < 0 or age > 18:
                continue
            fade = 1.0 - age / 18
            alpha = int(150 * fade)
            x, y = m.death_pos if m.death_pos is not None else m.pos
            r = m.radius * (1 + age * 0.04)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(140, 140, 145, alpha))

        # Alive marbles
        for m in self.marbles:
            if m.eliminated_frame is not None:
                continue
            x, y = m.pos
            r = m.radius
            # Winner glow if last alive
            still_alive = sum(1 for mm in self.marbles if mm.eliminated_frame is None)
            if still_alive == 1:
                for offset, alpha in [(12, 90), (6, 200)]:
                    draw.ellipse([x - r - offset, y - r - offset,
                                  x + r + offset, y + r + offset],
                                 outline=(*self.brand_gold, alpha), width=3)

            # Glossy fill
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
                      label, font=self.font_code,
                      fill="white", stroke_width=2, stroke_fill="black")

        # Chrome
        alive_count = sum(1 for m in self.marbles if m.eliminated_frame is None)
        self._draw_counter(img, alive_count, len(self.marbles))
        self._draw_round_chip(img)
        self._draw_watermark(img)

        # Hook band fades out by 2.7s
        if i < int(self.fps * 2.7):
            self._draw_banded(img, self.hook_text.upper(), self.font_hook,
                              int(self.h * 0.025))

        # CTA band always visible after intro
        if i >= int(self.fps * 0.5):
            self._draw_banded(img, self.cta_text.upper(), self.font_cta,
                              int(self.h * 0.94))

        # Payoff overlay once winner is decided
        self._draw_payoff(img, i)

        return img

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
            self.step(i)
