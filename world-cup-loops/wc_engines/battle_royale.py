"""Battle Royale engine — 48 country marbles, one survives.

Pure physics in a circular arena. Marbles bounce off arena walls + each
other. Eliminations are scheduled by frame (not by physics contact) so we
can deterministically pick the winner — the underdog narrative.

Visual mechanic:
- 48 marbles populate a circular arena, each country code + flag color
- Arena ring slowly shrinks (danger ring, red glow)
- Eliminations cascade: marbles fade to gray ghosts at scheduled frames
- Counter ticks down 48 → 1
- Winner (configured) carries a gold glow throughout
- Final 3s: payoff overlay with the survivor's story

No charts, no static cards. Motion is the content.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ----- font lookup -----

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
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
    )


def _hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


@dataclass
class Marble:
    code: str
    color: tuple
    pos: np.ndarray
    vel: np.ndarray
    radius: float
    is_winner: bool = False
    eliminated_frame: int | None = None
    death_pos: np.ndarray | None = None


class BattleRoyaleEngine:
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
        self.arena_r_start = cfg.get("arena_r_start", 480)
        self.arena_r_end = cfg.get("arena_r_end", 100)

        # Content
        self.hook_text = cfg.get("hook_text", "")
        self.cta_text = cfg.get("cta_text", "")
        self.brand_mark = cfg.get("brand_mark", "pitch.predict")
        self.payoff_main = cfg.get("payoff_main", "")
        self.payoff_sub = cfg.get("payoff_sub", "")
        self.round_chip = cfg.get("round_chip", "WC 2026 · GROUP C")

        # Teams
        rng = random.Random(seed)
        np_rng = np.random.default_rng(seed)
        teams = cfg["teams"]
        winner_code = cfg.get("winner_code", "CUR")

        self.marbles: list[Marble] = []
        spawn_r = self.arena_r_start * 0.70
        # Pre-distribute on a grid-ish ring then jitter to avoid initial overlap
        n = len(teams)
        for i, t in enumerate(teams):
            angle = (i / n) * 2 * math.pi + np_rng.uniform(-0.05, 0.05)
            r_init = spawn_r * (0.35 + np_rng.uniform(0, 0.55))
            pos = self.center + np.array([
                math.cos(angle) * r_init,
                math.sin(angle) * r_init,
            ])
            speed = np_rng.uniform(130, 230)
            v_angle = np_rng.uniform(0, 2 * math.pi)
            vel = np.array(
                [math.cos(v_angle) * speed, math.sin(v_angle) * speed],
                dtype=np.float64,
            )
            is_winner = (t["code"] == winner_code)
            # Underdog visual: WINNER is slightly smaller (vulnerable look),
            # but glows gold so viewers can track it.
            radius = 22 if is_winner else 28
            self.marbles.append(Marble(
                code=t["code"],
                color=_hex(t["color"]),
                pos=pos,
                vel=vel,
                radius=radius,
                is_winner=is_winner,
            ))

        # Elimination schedule: 47 marbles eliminated over the dramatic window
        intro_end = int(self.fps * 1.6)
        payoff_start = int(self.fps * 12.0)
        non_winners = [idx for idx, m in enumerate(self.marbles) if not m.is_winner]
        rng.shuffle(non_winners)
        n_elim = len(non_winners)
        elim_collision_frames = []
        for k in range(n_elim):
            t = k / max(n_elim - 1, 1)
            # Smoothstep: slow start (chaos) → fast mid → slow finale (drama)
            eased = 3 * t * t - 2 * t * t * t
            frame = intro_end + int((payoff_start - intro_end) * eased)
            elim_collision_frames.append(frame)
        for marble_idx, frame in zip(non_winners, elim_collision_frames):
            self.marbles[marble_idx].eliminated_frame = frame
        # Store the schedule for audio sync
        self.elimination_frames = sorted(elim_collision_frames)
        self.payoff_frame = payoff_start

        # Background cache
        self.bg_cache = self._render_background()

        # Fonts
        self.font_code = _font("inter_bold", 17)
        self.font_counter = _font("roboto_cond", 56)
        self.font_counter_label = _font("inter_semi", 22)
        self.font_hook = _font("anton", 76)
        self.font_cta = _font("anton", 52)
        self.font_brand = _font("inter_semi", 28)
        self.font_chip = _font("roboto_cond", 22)
        self.font_payoff_main = _font("anton", 150)
        self.font_payoff_sub = _font("inter_bold", 44)

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
        t = i / max(self.num_frames - 1, 1)
        # Shrink curve: slow early, accelerate late
        if t < 0.8:
            eased = (t / 0.8) ** 1.4 * 0.85
        else:
            local = (t - 0.8) / 0.2
            eased = 0.85 + local * 0.15
        return self.arena_r_start - (self.arena_r_start - self.arena_r_end) * eased

    def step(self, i: int):
        arena_r = self._arena_radius(i)

        # Move alive marbles
        alive = []
        for m in self.marbles:
            if m.eliminated_frame is not None and i >= m.eliminated_frame:
                if m.eliminated_frame == i and m.death_pos is None:
                    m.death_pos = m.pos.copy()
                continue
            m.pos += m.vel * self.dt

            offset = m.pos - self.center
            dist = float(np.linalg.norm(offset))
            max_dist = arena_r - m.radius
            if dist > max_dist and dist > 1e-6:
                normal = offset / dist
                m.pos = self.center + normal * max_dist
                vn = float(np.dot(m.vel, normal))
                if vn > 0:
                    m.vel -= 2 * vn * normal
            alive.append(m)

        # Marble-marble collisions (O(N²) — fine at N=48)
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
                    ma.pos -= normal * overlap * 0.5
                    mb.pos += normal * overlap * 0.5
                    rel = mb.vel - ma.vel
                    vn = float(np.dot(rel, normal))
                    if vn < 0:
                        ma.vel += vn * normal
                        mb.vel -= vn * normal

    # ----- drawing helpers -----

    def _draw_banded(self, img, text, font, y_top, alpha=180):
        draw = ImageDraw.Draw(img, "RGBA")
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad_x, pad_y = 36, 18
        x0 = (self.w - tw) // 2 - pad_x
        x1 = (self.w + tw) // 2 + pad_x
        y0 = y_top - pad_y
        y1 = y_top + th + pad_y
        draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, alpha))
        draw.text(
            ((self.w - tw) // 2, y_top),
            text,
            font=font,
            fill="white",
            stroke_width=3,
            stroke_fill="black",
        )

    def _draw_watermark(self, img):
        draw = ImageDraw.Draw(img, "RGBA")
        draw.text(
            (28, 28),
            self.brand_mark,
            font=self.font_brand,
            fill=(255, 255, 255, 165),
            stroke_width=2,
            stroke_fill=(0, 0, 0, 180),
        )

    def _draw_round_chip(self, img):
        draw = ImageDraw.Draw(img, "RGBA")
        text = self.round_chip
        bbox = draw.textbbox((0, 0), text, font=self.font_chip)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad_x, pad_y = 14, 8
        x0 = self.w - tw - 28 - pad_x
        x1 = self.w - 28 + pad_x
        y0 = 28
        y1 = 28 + th + pad_y * 2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=999, fill=(*self.brand_green, 230))
        draw.text((x0 + pad_x, y0 + pad_y - 2), text, font=self.font_chip, fill="white")

    def _draw_counter(self, img, alive_count: int, total: int):
        draw = ImageDraw.Draw(img, "RGBA")
        text = f"{alive_count:02d}"
        label = f"OF {total} ALIVE"
        # Position bottom-left of arena area
        x = 60
        y = 130
        # Number
        bbox = draw.textbbox((0, 0), text, font=self.font_counter)
        tw = bbox[2] - bbox[0]
        # Apply gold tint if only winner remains
        color = self.brand_gold if alive_count == 1 else (255, 255, 255)
        draw.text(
            (x, y),
            text,
            font=self.font_counter,
            fill=color,
            stroke_width=3,
            stroke_fill="black",
        )
        # Label below the number
        draw.text(
            (x + 4, y + 70),
            label,
            font=self.font_counter_label,
            fill=(218, 230, 223, 200),
        )

    def _draw_payoff(self, img, frame: int):
        """Overlay the final payoff message during the last ~3s."""
        if frame < self.payoff_frame:
            return
        fade = min((frame - self.payoff_frame) / 12, 1.0)
        # Scrim
        scrim = Image.new("RGBA", img.size, (0, 0, 0, int(200 * fade)))
        img.paste(scrim, (0, 0), scrim)

        draw = ImageDraw.Draw(img, "RGBA")
        main_text = self.payoff_main
        sub_text = self.payoff_sub

        # Main
        bbox = draw.textbbox((0, 0), main_text, font=self.font_payoff_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        cy = self.h // 2 - 80
        draw.text(
            ((self.w - tw) // 2, cy - th // 2),
            main_text,
            font=self.font_payoff_main,
            fill="white",
            stroke_width=5,
            stroke_fill="black",
        )

        # Sub
        sbbox = draw.textbbox((0, 0), sub_text, font=self.font_payoff_sub)
        stw = sbbox[2] - sbbox[0]
        sth = sbbox[3] - sbbox[1]
        draw.text(
            ((self.w - stw) // 2, cy + th // 2 + 30),
            sub_text,
            font=self.font_payoff_sub,
            fill=self.brand_gold,
            stroke_width=2,
            stroke_fill="black",
        )

    # ----- per-frame render -----

    def frame(self, i: int) -> Image.Image:
        img = self.bg_cache.copy()
        draw = ImageDraw.Draw(img, "RGBA")

        # Arena visuals
        arena_r = self._arena_radius(i)
        cx, cy = int(self.center[0]), int(self.center[1])
        # Outer-most arena hint (fixed reference)
        draw.ellipse(
            [cx - self.arena_r_start, cy - self.arena_r_start,
             cx + self.arena_r_start, cy + self.arena_r_start],
            outline=(255, 255, 255, 22), width=2,
        )
        # Active danger ring (shrinks)
        for offset, alpha in [(0, 200), (5, 100), (12, 50)]:
            draw.ellipse(
                [cx - arena_r - offset, cy - arena_r - offset,
                 cx + arena_r + offset, cy + arena_r + offset],
                outline=(*self.danger, alpha), width=2,
            )

        # Marble shadows (drawn first)
        for m in self.marbles:
            if m.eliminated_frame is not None and i > m.eliminated_frame + 18:
                continue
            if m.eliminated_frame is not None and i > m.eliminated_frame:
                continue  # ghost fading - skip shadow
            x, y = m.pos
            r = m.radius
            shadow = (0, 0, 0, 130)
            draw.ellipse([x - r * 0.95, y + r * 0.55, x + r * 0.95, y + r * 1.05], fill=shadow)

        # Ghosts of eliminated marbles
        for m in self.marbles:
            if m.eliminated_frame is None or i <= m.eliminated_frame:
                continue
            age = i - m.eliminated_frame
            if age > 18:
                continue
            fade = 1.0 - age / 18
            alpha = int(150 * fade)
            x, y = m.death_pos if m.death_pos is not None else m.pos
            r = m.radius * (1 + age * 0.04)  # slight bloom
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(140, 140, 145, alpha))

        # Alive marbles
        for m in self.marbles:
            if m.eliminated_frame is not None and i >= m.eliminated_frame:
                continue
            x, y = m.pos
            r = m.radius

            # Winner glow ring
            if m.is_winner:
                for offset, alpha in [(10, 110), (5, 200)]:
                    draw.ellipse(
                        [x - r - offset, y - r - offset, x + r + offset, y + r + offset],
                        outline=(*self.brand_gold, alpha), width=3,
                    )

            # Glossy fill
            color = m.color
            light = tuple(min(255, int(c * 1.5 + 60)) for c in color)
            dark = tuple(int(c * 0.55) for c in color)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=dark)
            for k in range(int(r), 0, -2):
                t = 1 - (k / r)
                blend = _lerp_color(dark, color, t)
                draw.ellipse([x - k, y - k, x + k, y + k], fill=blend)
            # Highlight
            hl = r * 0.42
            draw.ellipse(
                [x - hl - r * 0.22, y - hl - r * 0.22, x + hl - r * 0.22, y + hl - r * 0.22],
                fill=light,
            )
            # White outline
            draw.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 170), width=2)

            # Label (3-letter code)
            label = m.code
            bbox = draw.textbbox((0, 0), label, font=self.font_code)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                (x - tw / 2, y - th / 2 - 2),
                label,
                font=self.font_code,
                fill="white",
                stroke_width=2,
                stroke_fill="black",
            )

        # Chrome
        alive_count = sum(
            1 for m in self.marbles
            if not (m.eliminated_frame is not None and i >= m.eliminated_frame)
        )
        self._draw_counter(img, alive_count, len(self.marbles))
        self._draw_round_chip(img)
        self._draw_watermark(img)

        # Hook band (first 2.2s, fade out by 2.5s)
        if i < int(self.fps * 2.7):
            self._draw_banded(img, self.hook_text.upper(), self.font_hook,
                              int(self.h * 0.025))

        # CTA band (continuous bottom, fades in early)
        if i >= int(self.fps * 0.5):
            self._draw_banded(img, self.cta_text.upper(), self.font_cta,
                              int(self.h * 0.94))

        # Payoff overlay
        self._draw_payoff(img, i)

        return img

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
            self.step(i)
