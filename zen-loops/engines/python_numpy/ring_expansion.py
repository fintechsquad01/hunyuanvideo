"""Ring-bounce simulation — the most viral physics format on TikTok/Reels.

A ball bounces inside a circular ring. Each wall collision emits a melody
note (recorded as a frame index → synthesized to WAV → muxed into the
final MP4). The ring slowly grows over time, which accelerates the ball
(bigger radius = longer free flight = higher impact velocity = faster
pacing toward the end).

Two visual flourishes for retention:
- Each collision spawns a fading shockwave ring at the impact point
- A bounce counter ticks up in the corner ("BOUNCE: 47")

This engine is clean-room — implemented from physics first principles,
no code lifted from the unlicensed reference repos.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw

from engines.audio_reactive.collision_audio import MELODY_TITLES
from overlays.text_overlay import _fit_font, _load_font, _text_size


def _hex_to_rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


@dataclass
class Shockwave:
    pos: np.ndarray
    color: tuple[int, int, int]
    spawn_frame: int


class RingExpansionEngine:
    """Ball-in-growing-ring.

    Config schema:
        ball_radius: int          (default 38)
        ball_color: hex
        ball_speed: float         initial speed in px/s (default 900)
        ring_color: hex
        ring_thickness: int       (default 14)
        ring_radius_start_pct: float  initial inner radius as % of min(w,h)/2 (default 0.55)
        ring_radius_end_pct: float    final inner radius as % of min(w,h)/2 (default 0.85)
        center: [x, y]            (default = canvas center)
        speed_gain_per_bounce: float  multiplier per collision (default 1.005)
        melody: melody name from collision_audio.MELODIES (default 'twinkle')
        counter: bool             show bounce counter (default True)
    """

    def __init__(self, cfg: dict, seed: int = 11):
        self.w, self.h = cfg["resolution"]
        self.duration = cfg["duration"]
        self.fps = cfg["fps"]
        self.bg = _hex_to_rgb(cfg.get("background", "#0a0a14"))
        self.num_frames = self.duration * self.fps
        self.dt = 1.0 / self.fps

        center_cfg = cfg.get("center")
        if center_cfg:
            self.center = np.array(center_cfg, dtype=np.float64)
        else:
            self.center = np.array([self.w / 2, self.h / 2], dtype=np.float64)

        max_inner = min(self.w, self.h) / 2 - 40
        self.r_start = max_inner * cfg.get("ring_radius_start_pct", 0.55)
        self.r_end = max_inner * cfg.get("ring_radius_end_pct", 0.85)

        self.ring_thickness = cfg.get("ring_thickness", 14)
        self.ring_color = _hex_to_rgb(cfg.get("ring_color", "#3bcfff"))
        self.ball_radius = cfg.get("ball_radius", 38)
        self.ball_color = _hex_to_rgb(cfg.get("ball_color", "#ff3b3b"))
        self.speed_gain = cfg.get("speed_gain_per_bounce", 1.005)

        rng = random.Random(seed)
        angle = rng.uniform(0, 2 * math.pi)
        speed = float(cfg.get("ball_speed", 900))
        self.ball_pos = self.center.copy()
        self.ball_vel = np.array([math.cos(angle) * speed, math.sin(angle) * speed], dtype=np.float64)

        self.melody_name = cfg.get("melody", "twinkle")
        self.collision_frames: list[int] = []
        self.shockwaves: list[Shockwave] = []
        self.show_counter = cfg.get("counter", True)

        reveal_pct = cfg.get("reveal_start_pct", 0.83)
        self.reveal_start_frame = int(self.num_frames * reveal_pct)
        explicit_reveal = cfg.get("reveal_text")
        if explicit_reveal is None and cfg.get("reveal", True):
            explicit_reveal = MELODY_TITLES.get(self.melody_name)
        self.reveal_text = explicit_reveal

        self.counter_font = _load_font(54)
        self.reveal_label_font = _load_font(110)
        self.reveal_caption_font = _load_font(48)

        rng_conf = random.Random(seed + 1)
        self._confetti_seeds = [
            (rng_conf.uniform(0, self.w), rng_conf.uniform(0, self.h * 0.55),
             rng_conf.uniform(-1, 1), rng_conf.uniform(0.3, 1.6),
             rng_conf.choice([
                 (255, 90, 90), (90, 200, 255), (255, 220, 80),
                 (180, 120, 255), (90, 255, 170), (255, 140, 60),
             ]))
            for _ in range(80)
        ]

    def _current_ring_radius(self, i: int) -> float:
        t = i / max(self.num_frames - 1, 1)
        return self.r_start + (self.r_end - self.r_start) * t

    def step(self, i: int):
        self.ball_pos += self.ball_vel * self.dt

        delta = self.ball_pos - self.center
        dist = float(np.linalg.norm(delta))
        ring_r = self._current_ring_radius(i)
        max_dist = ring_r - self.ball_radius

        if dist > max_dist and dist > 1e-6:
            normal = delta / dist
            self.ball_pos = self.center + normal * max_dist
            vn = float(np.dot(self.ball_vel, normal))
            if vn > 0:
                self.ball_vel -= 2 * vn * normal
                self.ball_vel *= self.speed_gain
                self.collision_frames.append(i)
                impact = self.center + normal * ring_r
                self.shockwaves.append(
                    Shockwave(pos=impact, color=self.ball_color, spawn_frame=i)
                )

    def frame(self, i: int) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), self.bg)
        draw = ImageDraw.Draw(img)

        ring_r = self._current_ring_radius(i)
        cx, cy = self.center
        for offset in range(self.ring_thickness):
            r = ring_r + offset
            alpha_factor = 1.0 - offset / max(self.ring_thickness, 1)
            color = tuple(int(c * (0.5 + 0.5 * alpha_factor)) for c in self.ring_color)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)

        active = []
        for sw in self.shockwaves:
            age = i - sw.spawn_frame
            if age < 0 or age > 18:
                continue
            radius = self.ball_radius + age * 6
            x, y = sw.pos
            fade = max(0, 255 - age * 14)
            color = tuple(int(c * fade / 255) for c in sw.color)
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], outline=color, width=3)
            active.append(sw)
        self.shockwaves = active

        bx, by = self.ball_pos
        r = self.ball_radius
        draw.ellipse(
            [bx - r, by - r, bx + r, by + r],
            fill=self.ball_color,
            outline="white",
            width=3,
        )

        if self.show_counter:
            text = f"{len(self.collision_frames):03d}"
            bbox = draw.textbbox((0, 0), text, font=self.counter_font)
            tw = bbox[2] - bbox[0]
            draw.text(
                (self.w - tw - 48, 48),
                text,
                font=self.counter_font,
                fill="white",
                stroke_width=3,
                stroke_fill="black",
            )

        if self.reveal_text and i >= self.reveal_start_frame:
            self._draw_reveal(img, draw, i)

        return img

    def _draw_reveal(self, img: Image.Image, draw: ImageDraw.ImageDraw, i: int):
        age = i - self.reveal_start_frame
        total_reveal_frames = max(self.num_frames - self.reveal_start_frame, 1)
        progress = min(age / max(total_reveal_frames * 0.4, 1), 1.0)
        scrim_alpha = int(180 * progress)
        scrim = Image.new("RGBA", img.size, (0, 0, 0, scrim_alpha))
        img.paste(scrim, (0, 0), scrim)

        for x0, y0, vx, vy, color in self._confetti_seeds:
            t = age * 0.08
            x = (x0 + vx * 240 * t) % self.w
            y = (y0 + (vy * 70 + age * 6))
            if y < 0 or y > self.h:
                continue
            r = 6
            ImageDraw.Draw(img).ellipse([x - r, y - r, x + r, y + r], fill=color)

        draw = ImageDraw.Draw(img)
        caption = "It was"
        cap_bbox = draw.textbbox((0, 0), caption, font=self.reveal_caption_font)
        cap_w = cap_bbox[2] - cap_bbox[0]
        cap_h = cap_bbox[3] - cap_bbox[1]
        cy_caption = self.h // 2 - 90
        draw.text(
            ((self.w - cap_w) // 2, cy_caption),
            caption,
            font=self.reveal_caption_font,
            fill="white",
            stroke_width=2,
            stroke_fill="black",
        )

        safe_w = int(self.w * 0.86)
        title_font = _fit_font(self.reveal_text, safe_w, start_size=130, min_size=48)
        tw, th = _text_size(draw, self.reveal_text, title_font)
        cy_title = cy_caption + cap_h + 30
        draw.text(
            ((self.w - tw) // 2, cy_title),
            self.reveal_text,
            font=title_font,
            fill="white",
            stroke_width=5,
            stroke_fill="black",
        )

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
            self.step(i)
