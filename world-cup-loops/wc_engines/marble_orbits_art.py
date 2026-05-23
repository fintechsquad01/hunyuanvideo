"""Marble Orbits — pure generative art loop (no chrome, no captions).

32 WC2026 country-colored marbles orbit a central gravitational attractor.
Mass-weighted elastic collisions add chaos. Each marble paints a fading
trail into an accumulation buffer, producing a kaleidoscope painting
that evolves over the loop.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image


def _hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class MarbleOrbitsArtEngine:
    def __init__(self, cfg: dict, seed: int = 11):
        self.w, self.h = cfg["resolution"]
        self.fps = cfg["fps"]
        self.duration = cfg["duration"]
        self.num_frames = int(self.duration * self.fps)
        self.dt = 1.0 / self.fps

        # Background gradient
        bg_top = _hex(cfg.get("bg_top", "#0a1b14"))
        bg_mid = _hex(cfg.get("bg_mid", "#06120c"))
        bg_bot = _hex(cfg.get("bg_bot", "#02060a"))
        self.bg = self._make_bg(bg_top, bg_mid, bg_bot)

        # Physics
        self.G = cfg.get("G", 9000.0)
        self.center_mass = cfg.get("center_mass", 220000.0)
        self.center = np.array([self.w / 2, self.h / 2], dtype=np.float64)
        self.trail_fade = cfg.get("trail_fade", 0.955)
        self.softening = cfg.get("softening", 50.0)

        # Teams
        teams = cfg["teams"]
        n = len(teams)
        elos = [t["elo"] for t in teams]
        min_e, max_e = min(elos), max(elos)
        e_range = max(max_e - min_e, 1)

        rng = np.random.default_rng(seed)
        self.positions = np.zeros((n, 2), dtype=np.float64)
        self.velocities = np.zeros((n, 2), dtype=np.float64)
        self.radii = np.zeros(n)
        self.masses = np.zeros(n)
        self.colors = np.zeros((n, 3), dtype=np.float32)

        min_r = cfg.get("marble_min_radius", 7)
        max_r = cfg.get("marble_max_radius", 16)
        self.stamp_intensity = cfg.get("stamp_intensity", 165.0)
        jitter_lo = cfg.get("orbital_jitter_low", 0.82)
        jitter_hi = cfg.get("orbital_jitter_high", 1.08)

        for i, t in enumerate(teams):
            elo_t = (t["elo"] - min_e) / e_range
            r = min_r + elo_t * (max_r - min_r)
            self.radii[i] = r
            self.masses[i] = r ** 2
            self.colors[i] = np.array(_hex(t["color"]), dtype=np.float32)

            # Stagger orbits across multiple shells for visual variety
            shell = i % 5
            base_r = [220, 320, 430, 560, 700][shell]
            jitter = float(rng.uniform(-30, 40))
            spawn_r = base_r + jitter
            angle = (i / n) * 2 * math.pi + float(rng.uniform(-0.08, 0.08))
            self.positions[i] = self.center + spawn_r * np.array([
                math.cos(angle), math.sin(angle)])

            # Tangential velocity for ~circular orbit, jittered for ellipticals
            v_circ = math.sqrt(self.G * self.center_mass / spawn_r)
            v_circ *= float(rng.uniform(jitter_lo, jitter_hi))
            tangent = np.array([-math.sin(angle), math.cos(angle)])
            # 70% prograde, 30% retrograde — counter-rotating marbles cross
            if rng.uniform(0, 1) < 0.30:
                tangent = -tangent
            self.velocities[i] = tangent * v_circ

        # Accumulation buffer
        self.trail = np.zeros((self.h, self.w, 3), dtype=np.float32)

        # Previous positions (for sub-frame interpolation of trails)
        self.prev_positions = self.positions.copy()
        self.substeps = cfg.get("trail_substeps", 6)

        # Pre-render a stamp kernel for each marble radius (cached)
        self._stamp_cache: dict[int, np.ndarray] = {}

    # ----- helpers -----

    def _make_bg(self, top, mid, bot) -> np.ndarray:
        bg = np.zeros((self.h, self.w, 3), dtype=np.float32)
        for y in range(self.h):
            t = y / max(self.h - 1, 1)
            if t < 0.5:
                color = _lerp_color(top, mid, t / 0.5)
            else:
                color = _lerp_color(mid, bot, (t - 0.5) / 0.5)
            bg[y, :, :] = color
        # Subtle vignette toward edges
        cx, cy = self.w / 2, self.h / 2
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        max_d = np.sqrt(cx ** 2 + cy ** 2)
        vignette = np.clip(1.0 - (dist / max_d) ** 1.6 * 0.55, 0.45, 1.0)
        bg *= vignette[..., None]
        return bg

    def _get_stamp(self, r_int: int) -> np.ndarray:
        """Pre-rendered soft circle of unit color (HxWx1)."""
        if r_int in self._stamp_cache:
            return self._stamp_cache[r_int]
        span = max(int(r_int * 3.0), 4)
        size = span * 2 + 1
        yy, xx = np.mgrid[0:size, 0:size]
        cy = cx = span
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        # Sharp core + soft glow
        core = np.clip(1.0 - (dist / (r_int * 0.85)), 0, 1) ** 0.6  # bright core
        glow = np.clip(1.0 - (dist / (r_int * 3.0)) ** 1.8, 0, 1) * 0.45
        stamp = np.clip(core * 0.9 + glow, 0, 1.6).astype(np.float32)
        self._stamp_cache[r_int] = stamp
        return stamp

    def _add_stamp(self, cx: float, cy: float, r_int: int,
                   color: np.ndarray, intensity: float | None = None):
        if intensity is None:
            intensity = self.stamp_intensity
        stamp = self._get_stamp(r_int)
        ss = stamp.shape[0]
        half = ss // 2
        x0 = int(cx) - half
        y0 = int(cy) - half
        x1 = x0 + ss
        y1 = y0 + ss
        # Clip
        sx0 = max(0, -x0)
        sy0 = max(0, -y0)
        sx1 = ss - max(0, x1 - self.w)
        sy1 = ss - max(0, y1 - self.h)
        dx0 = max(0, x0)
        dy0 = max(0, y0)
        dx1 = min(self.w, x1)
        dy1 = min(self.h, y1)
        if dx1 <= dx0 or dy1 <= dy0:
            return
        s = stamp[sy0:sy1, sx0:sx1, None]  # (h,w,1)
        self.trail[dy0:dy1, dx0:dx1, :] += s * color[None, None, :] * (intensity / 255.0)

    # ----- physics -----

    def step(self):
        # Gravity toward center
        delta = self.center - self.positions
        dist = np.linalg.norm(delta, axis=1, keepdims=True)
        dist_safe = np.maximum(dist, self.softening)
        force_dir = delta / dist_safe
        a = self.G * self.center_mass / (dist_safe ** 2) * force_dir
        self.velocities += a * self.dt
        self.positions += self.velocities * self.dt

        # Pairwise collisions
        n = len(self.positions)
        for i in range(n):
            for j in range(i + 1, n):
                d = self.positions[j] - self.positions[i]
                dist = float(np.linalg.norm(d))
                min_d = self.radii[i] + self.radii[j]
                if dist < min_d and dist > 1e-6:
                    normal = d / dist
                    overlap = min_d - dist
                    total = self.masses[i] + self.masses[j]
                    self.positions[i] -= normal * overlap * (self.masses[j] / total)
                    self.positions[j] += normal * overlap * (self.masses[i] / total)
                    v1n = float(np.dot(self.velocities[i], normal))
                    v2n = float(np.dot(self.velocities[j], normal))
                    if v1n - v2n > 0:
                        continue
                    new_v1n = (v1n * (self.masses[i] - self.masses[j]) + 2 * self.masses[j] * v2n) / total
                    new_v2n = (v2n * (self.masses[j] - self.masses[i]) + 2 * self.masses[i] * v1n) / total
                    self.velocities[i] += (new_v1n - v1n) * normal
                    self.velocities[j] += (new_v2n - v2n) * normal

    def _paint(self):
        # Sub-frame interpolation: stamp marble at N points along its prev->curr
        # path so high-speed orbits read as continuous arcs, not dotted lines.
        sub = max(self.substeps, 1)
        per_step_intensity = self.stamp_intensity / sub
        for k in range(len(self.positions)):
            r_int = int(self.radii[k])
            color = self.colors[k]
            for s in range(sub):
                t = (s + 1) / sub
                px = self.prev_positions[k, 0] + t * (self.positions[k, 0] - self.prev_positions[k, 0])
                py = self.prev_positions[k, 1] + t * (self.positions[k, 1] - self.prev_positions[k, 1])
                self._add_stamp(px, py, r_int, color, intensity=per_step_intensity)
        # Snapshot for next frame
        self.prev_positions = self.positions.copy()

    def frame(self) -> Image.Image:
        # Composite trail over bg additively
        out = self.bg + self.trail
        out = np.clip(out, 0, 255).astype(np.uint8)
        return Image.fromarray(out)

    def __iter__(self):
        # Warm-up so trails are established before frame 0
        warmup = int(self.fps * 2.5)
        for _ in range(warmup):
            self.step()
            self.trail *= self.trail_fade
            self._paint()

        for _ in range(self.num_frames):
            self.trail *= self.trail_fade
            self._paint()
            yield self.frame()
            self.step()
