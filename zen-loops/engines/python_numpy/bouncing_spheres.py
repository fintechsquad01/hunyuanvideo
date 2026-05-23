"""Deterministic bouncing-sphere engine.

Produces a sequence of PIL.Image frames for a config-driven simulation.
The motion is intentionally deterministic given a fixed seed so reels can be
reproduced and A/B-tested.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw


def _hex_to_rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


@dataclass
class Sphere:
    pos: np.ndarray
    vel: np.ndarray
    radius: float
    color: tuple[int, int, int]


class BouncingSpheresEngine:
    def __init__(self, cfg: dict, seed: int = 42):
        self.w, self.h = cfg["resolution"]
        self.duration = cfg["duration"]
        self.fps = cfg["fps"]
        self.palette = [_hex_to_rgb(c) for c in cfg["palette"]]
        self.bg = _hex_to_rgb(cfg.get("background", "#0a0a14"))
        self.difficulty = cfg.get("difficulty", 3)
        self.num_frames = self.duration * self.fps

        rng = random.Random(seed)
        np_rng = np.random.default_rng(seed)

        n = 40 + self.difficulty * 15
        self.spheres: list[Sphere] = []
        for _ in range(n):
            radius = float(np_rng.integers(18, 36))
            pos = np.array(
                [
                    np_rng.uniform(radius, self.w - radius),
                    np_rng.uniform(radius, self.h - radius),
                ],
                dtype=np.float64,
            )
            speed = 200 + self.difficulty * 60
            angle = np_rng.uniform(0, 2 * np.pi)
            vel = np.array([np.cos(angle), np.sin(angle)], dtype=np.float64) * speed
            color = rng.choice(self.palette)
            self.spheres.append(Sphere(pos=pos, vel=vel, radius=radius, color=color))

        self.dt = 1.0 / self.fps

    def step(self):
        for s in self.spheres:
            s.pos += s.vel * self.dt
            if s.pos[0] - s.radius < 0:
                s.pos[0] = s.radius
                s.vel[0] *= -1
            elif s.pos[0] + s.radius > self.w:
                s.pos[0] = self.w - s.radius
                s.vel[0] *= -1
            if s.pos[1] - s.radius < 0:
                s.pos[1] = s.radius
                s.vel[1] *= -1
            elif s.pos[1] + s.radius > self.h:
                s.pos[1] = self.h - s.radius
                s.vel[1] *= -1

    def frame(self, i: int) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), self.bg)
        draw = ImageDraw.Draw(img)
        for s in self.spheres:
            x, y = s.pos
            r = s.radius
            draw.ellipse([x - r, y - r, x + r, y + r], fill=s.color)
        return img

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
            self.step()
