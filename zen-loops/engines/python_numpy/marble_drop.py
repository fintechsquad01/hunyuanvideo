"""Plinko-style marble race with identity labels.

Vertical canvas. A row of labeled marbles drops from the top through a Galton
board of pegs and lands in a finish zone at the bottom. The first marble to
cross the finish line wins, and a winner banner is drawn for the final ~2s.

This is the dominant viral format in the satisfying-simulation niche
(#chooseyourcolor, #marblerace). Identity labels (birth months, zodiacs,
initials, countries) turn passive viewers into commenters because the result
is *about them*.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from overlays.text_overlay import _load_font


def _hex_to_rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


@dataclass
class Marble:
    pos: np.ndarray
    vel: np.ndarray
    radius: float
    color: tuple[int, int, int]
    label: str
    finished: bool = False
    finish_frame: int | None = None


@dataclass
class Peg:
    pos: np.ndarray
    radius: float


class MarbleDropEngine:
    """Plinko marble race.

    Config schema:
        labels: list[str]      one label per marble (e.g. ["JAN", "FEB", ...])
        palette: list[hex]     one color per marble (cycles if shorter)
        peg_rows: int          how many rows of pegs (default 14)
        peg_spacing: int       px spacing between pegs (default 90)
        gravity: float         px/s^2 (default 1800)
        marble_radius: int     px (default 34)
        peg_radius: int        px (default 8)
        bounce: float          coefficient of restitution (default 0.55)
        finish_y_pct: float    finish line as fraction of height (default 0.92)
    """

    def __init__(self, cfg: dict, seed: int = 7):
        self.w, self.h = cfg["resolution"]
        self.duration = cfg["duration"]
        self.fps = cfg["fps"]
        self.bg = _hex_to_rgb(cfg.get("background", "#0a0a14"))
        self.num_frames = self.duration * self.fps
        self.dt = 1.0 / self.fps

        self.labels = cfg["labels"]
        palette = [_hex_to_rgb(c) for c in cfg["palette"]]
        self.colors = [palette[i % len(palette)] for i in range(len(self.labels))]

        self.gravity = cfg.get("gravity", 1800)
        self.marble_radius = cfg.get("marble_radius", 34)
        self.peg_radius = cfg.get("peg_radius", 8)
        self.bounce = cfg.get("bounce", 0.55)
        self.peg_rows = cfg.get("peg_rows", 14)
        self.peg_spacing = cfg.get("peg_spacing", 90)
        self.finish_y = int(self.h * cfg.get("finish_y_pct", 0.92))

        self.rng = random.Random(seed)
        np_rng = np.random.default_rng(seed)

        self.pegs = self._build_pegs()
        self.marbles = self._build_marbles(np_rng)
        self.winner: Marble | None = None
        self.winner_label_font = _load_font(140)
        self.banner_font = _load_font(56)
        self.label_font = _load_font(28)
        self.counter_font = _load_font(44)

    def _build_pegs(self) -> list[Peg]:
        pegs: list[Peg] = []
        top_y = int(self.h * 0.20)
        bottom_y = int(self.h * 0.82)
        rows = self.peg_rows
        row_step = (bottom_y - top_y) / max(rows - 1, 1)
        for row in range(rows):
            y = top_y + row * row_step
            offset = (self.peg_spacing / 2) if row % 2 == 1 else 0
            cols = self.w // self.peg_spacing
            for col in range(-1, cols + 1):
                x = col * self.peg_spacing + offset + (self.peg_spacing / 2)
                if 0 < x < self.w:
                    pegs.append(Peg(pos=np.array([x, y], dtype=np.float64), radius=self.peg_radius))
        return pegs

    def _build_marbles(self, np_rng) -> list[Marble]:
        n = len(self.labels)
        margin = self.marble_radius * 2
        positions_x = np.linspace(margin, self.w - margin, n)
        marbles: list[Marble] = []
        start_y = int(self.h * 0.14)
        for i, (label, color) in enumerate(zip(self.labels, self.colors)):
            jitter = np_rng.uniform(-4, 4)
            pos = np.array([positions_x[i] + jitter, start_y], dtype=np.float64)
            vel = np.array([0.0, 0.0], dtype=np.float64)
            marbles.append(Marble(pos=pos, vel=vel, radius=self.marble_radius, color=color, label=label))
        return marbles

    def _resolve_peg_collisions(self, m: Marble):
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
                    tangent = np.array([-normal[1], normal[0]])
                    m.vel += tangent * self.rng.uniform(-30, 30)

    def _resolve_marble_collisions(self):
        n = len(self.marbles)
        for i in range(n):
            a = self.marbles[i]
            if a.finished:
                continue
            for j in range(i + 1, n):
                b = self.marbles[j]
                if b.finished:
                    continue
                delta = b.pos - a.pos
                dist = float(np.linalg.norm(delta))
                min_dist = a.radius + b.radius
                if dist < min_dist and dist > 1e-6:
                    normal = delta / dist
                    overlap = min_dist - dist
                    a.pos -= normal * overlap / 2
                    b.pos += normal * overlap / 2
                    rel_vel = b.vel - a.vel
                    vn = float(np.dot(rel_vel, normal))
                    if vn < 0:
                        impulse = (1 + self.bounce) * vn * normal
                        a.vel += impulse / 2
                        b.vel -= impulse / 2

    def step(self, frame_idx: int):
        for m in self.marbles:
            if m.finished:
                continue
            m.vel[1] += self.gravity * self.dt
            m.pos += m.vel * self.dt

            if m.pos[0] - m.radius < 0:
                m.pos[0] = m.radius
                m.vel[0] *= -self.bounce
            elif m.pos[0] + m.radius > self.w:
                m.pos[0] = self.w - m.radius
                m.vel[0] *= -self.bounce

            self._resolve_peg_collisions(m)

            if m.pos[1] + m.radius >= self.finish_y and not m.finished:
                m.finished = True
                m.finish_frame = frame_idx
                if self.winner is None:
                    self.winner = m

        self._resolve_marble_collisions()

    def _draw_label(self, draw: ImageDraw.ImageDraw, m: Marble):
        bbox = draw.textbbox((0, 0), m.label, font=self.label_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = m.pos[0] - tw / 2
        y = m.pos[1] - th / 2 - 2
        draw.text(
            (x, y),
            m.label,
            font=self.label_font,
            fill="white",
            stroke_width=2,
            stroke_fill="black",
        )

    def _draw_counter(self, draw: ImageDraw.ImageDraw):
        remaining = sum(1 for m in self.marbles if not m.finished)
        total = len(self.marbles)
        text = f"{remaining}/{total} racing"
        bbox = draw.textbbox((0, 0), text, font=self.counter_font)
        tw = bbox[2] - bbox[0]
        x = self.w - tw - 40
        y = 40
        draw.text(
            (x, y),
            text,
            font=self.counter_font,
            fill="white",
            stroke_width=2,
            stroke_fill="black",
        )

    def _draw_winner_banner(self, img: Image.Image, draw: ImageDraw.ImageDraw):
        if self.winner is None:
            return
        text = self.winner.label
        bbox = draw.textbbox((0, 0), text, font=self.winner_label_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        center_y = self.h // 2
        pad_x, pad_y = 80, 40
        box = [
            (self.w - tw) // 2 - pad_x,
            center_y - th // 2 - pad_y,
            (self.w + tw) // 2 + pad_x,
            center_y + th // 2 + pad_y,
        ]
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        odraw.rectangle(box, fill=(0, 0, 0, 200))
        img.paste(overlay, (0, 0), overlay)

        banner = "WINNER"
        bb_bbox = draw.textbbox((0, 0), banner, font=self.banner_font)
        bb_w = bb_bbox[2] - bb_bbox[0]
        draw.text(
            ((self.w - bb_w) // 2, box[1] - 60),
            banner,
            font=self.banner_font,
            fill=self.winner.color,
            stroke_width=3,
            stroke_fill="black",
        )
        draw.text(
            ((self.w - tw) // 2, center_y - th // 2 - 10),
            text,
            font=self.winner_label_font,
            fill="white",
            stroke_width=5,
            stroke_fill="black",
        )

    def frame(self, i: int) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), self.bg)
        draw = ImageDraw.Draw(img)

        finish_color = (255, 255, 255)
        draw.line([(0, self.finish_y), (self.w, self.finish_y)], fill=finish_color, width=3)
        for x in range(0, self.w, 60):
            checker_y = self.finish_y + ((x // 60) % 2) * 18
            draw.rectangle([x, checker_y, x + 30, checker_y + 18], fill="white")

        for peg in self.pegs:
            x, y = peg.pos
            r = peg.radius
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(120, 120, 130))

        for m in self.marbles:
            x, y = m.pos
            r = m.radius
            if m.finished and m is not self.winner:
                color = tuple(c // 3 for c in m.color)
            else:
                color = m.color
            draw.ellipse(
                [x - r, y - r, x + r, y + r],
                fill=color,
                outline="white",
                width=3,
            )
            self._draw_label(draw, m)

        self._draw_counter(draw)

        if self.winner is not None and self.winner.finish_frame is not None:
            frames_since_win = i - self.winner.finish_frame
            if frames_since_win >= 0:
                self._draw_winner_banner(img, ImageDraw.Draw(img))

        return img

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
            self.step(i)
