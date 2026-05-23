"""Bracket Knockout — HONEST single-elimination physics (per PIECE_LOCK.md).

16 top WC2026 qualifiers seeded by real Elo. Single-elimination bracket:
R16 (8 matches) → QF (4) → SF (2) → Final (1).

Each match is a head-to-head sumo duel in a small circular ring:
- Two marbles spawn on opposite sides
- Initial velocity pointed at each other, magnitude proportional to Elo
- Mass-weighted elastic collisions (radius ∝ Elo, mass = radius²)
- Loser = first marble whose center exits the ring for >10 consecutive frames
- Hard cap per match (3.5s) — if neither out, marble closer to center survives

No `winner_code` config. The physics decides every match.
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


# Standard 16-team seeding pairs (1v16, 8v9, 5v12, 4v13, 6v11, 3v14, 7v10, 2v15)
SEED_ORDER = [0, 15, 7, 8, 4, 11, 3, 12, 5, 10, 2, 13, 6, 9, 1, 14]


@dataclass
class MatchMarble:
    code: str
    color: tuple
    elo: int
    radius: float
    mass: float
    pos: np.ndarray
    vel: np.ndarray
    outside_frames: int = 0


@dataclass
class MatchResult:
    team_a: dict
    team_b: dict
    winner_idx: int          # 0 or 1
    duration_frames: int     # frames until decided
    trajectory: list         # per-frame [(pos_a, pos_b)] np arrays
    decision_frame: int      # frame within match when loser was eliminated


class BracketHonestEngine:
    def __init__(self, cfg: dict, seed: int = 7):
        self.w, self.h = cfg["resolution"]
        self.fps = cfg["fps"]
        self.dt = 1.0 / self.fps

        # Brand palette
        self.bg_top = _hex(cfg.get("bg_top", "#0d2818"))
        self.bg_mid = _hex(cfg.get("bg_mid", "#08180e"))
        self.bg_bot = _hex(cfg.get("bg_bot", "#020a05"))
        self.brand_gold = _hex(cfg.get("brand_gold", "#ffd400"))
        self.danger = _hex(cfg.get("danger", "#ff4d4d"))
        self.brand_green = _hex(cfg.get("brand_green", "#0f9d58"))

        # Layout
        self.ring_cx = self.w // 2
        self.ring_cy = cfg.get("ring_cy", 760)
        self.ring_r = cfg.get("ring_r", 360)

        # Marble sizing
        self.min_r = cfg.get("marble_min_radius", 36)
        self.max_r = cfg.get("marble_max_radius", 72)
        self.min_speed = cfg.get("marble_min_speed", 280)
        self.max_speed = cfg.get("marble_max_speed", 520)

        # Chrome
        self.hook_text = cfg.get("hook_text", "")
        self.cta_text = cfg.get("cta_text", "")
        self.brand_mark = cfg.get("brand_mark", "pitch.predict")
        self.round_chip = cfg.get("round_chip", "WC 2026 · BRACKET")

        # Teams — take top 16 by Elo from config
        teams = sorted(cfg["teams"], key=lambda t: -t["elo"])[:16]
        elos = [t["elo"] for t in teams]
        min_elo, max_elo = min(elos), max(elos)
        elo_range = max(max_elo - min_elo, 1)
        for t in teams:
            t["elo_t"] = (t["elo"] - min_elo) / elo_range
        self.r16_teams = [teams[i] for i in SEED_ORDER]

        self.np_rng = np.random.default_rng(seed)
        self.seed = seed

        # ---- Pre-simulate the whole bracket ----
        self.matches: list[MatchResult] = []
        self.round_starts: list[int] = []  # match index where each round begins
        self.intro_frames = int(self.fps * 1.0)
        self.transition_frames = int(self.fps * 0.4)

        current = list(self.r16_teams)
        round_names = ["R16", "QF", "SF", "F"]
        match_seed = seed * 1000
        round_match_counts = []
        for round_name in round_names:
            self.round_starts.append(len(self.matches))
            round_match_counts.append(len(current) // 2)
            next_round = []
            for k in range(0, len(current), 2):
                ma = self._simulate_match(current[k], current[k+1], match_seed)
                self.matches.append(ma)
                next_round.append(ma.team_a if ma.winner_idx == 0 else ma.team_b)
                match_seed += 1
            current = next_round
        self.round_names = round_names
        self.round_match_counts = round_match_counts
        self.champion = current[0]

        # ---- Build timeline ----
        # frame -> (match_idx, local_frame, is_transition_after_match)
        cursor = self.intro_frames
        self.match_starts: list[int] = []
        self.match_decision_frames: list[int] = []  # global frame when decided
        for m in self.matches:
            self.match_starts.append(cursor)
            self.match_decision_frames.append(cursor + m.decision_frame)
            cursor += m.duration_frames + self.transition_frames
        self.winner_frame = cursor
        self.payoff_frames = int(self.fps * 4.5)
        self.num_frames = cursor + self.payoff_frames
        self.duration = self.num_frames / self.fps

        # Fonts
        self.font_code_match = _font("inter_bold", 28)
        self.font_round_label = _font("anton", 56)
        self.font_match_idx = _font("inter_semi", 22)
        self.font_bracket_code = _font("inter_bold", 13)
        self.font_hook = _font("anton", 64)
        self.font_cta = _font("anton", 46)
        self.font_brand = _font("inter_semi", 28)
        self.font_chip = _font("roboto_cond", 22)
        self.font_payoff_main = _font("anton", 220)
        self.font_payoff_sub = _font("inter_bold", 42)
        self.font_payoff_eyebrow = _font("roboto_cond", 30)

        # Cache bg
        self.bg_cache = self._render_background()

        # Tick frames for audio sync (collision events approximated as decision_frames)
        self.collision_frames = list(self.match_decision_frames)

    # ===== Sub-match physics =====

    def _simulate_match(self, team_a: dict, team_b: dict, seed: int) -> MatchResult:
        """Run a head-to-head sumo until one marble exits the ring."""
        rng = np.random.default_rng(seed)

        def make_marble(team: dict, side: int) -> MatchMarble:
            elo_t = team["elo_t"]
            radius = self.min_r + elo_t * (self.max_r - self.min_r)
            mass = radius ** 2
            speed = self.min_speed + elo_t * (self.max_speed - self.min_speed)
            speed *= float(rng.uniform(0.92, 1.10))
            # Spawn near edge, pointing inward + small tangent
            spawn_angle = 0 if side == 0 else math.pi  # left or right
            spawn_offset = self.ring_r * 0.75
            pos = np.array([
                self.ring_cx + math.cos(spawn_angle) * spawn_offset,
                self.ring_cy + math.sin(spawn_angle) * spawn_offset,
            ], dtype=np.float64)
            # Velocity pointing at center (with small tangent jitter)
            to_center = np.array([self.ring_cx, self.ring_cy], dtype=np.float64) - pos
            to_center /= max(np.linalg.norm(to_center), 1e-6)
            tangent_angle = float(rng.uniform(-0.45, 0.45))
            ca, sa = math.cos(tangent_angle), math.sin(tangent_angle)
            direction = np.array([
                to_center[0] * ca - to_center[1] * sa,
                to_center[0] * sa + to_center[1] * ca,
            ])
            vel = direction * speed
            return MatchMarble(
                code=team["code"], color=_hex(team["color"]),
                elo=team["elo"], radius=radius, mass=mass,
                pos=pos, vel=vel,
            )

        ma = make_marble(team_a, 0)
        mb = make_marble(team_b, 1)

        max_frames = int(self.fps * 3.5)
        trajectory = []
        winner_idx = None
        decision_frame = max_frames - 1

        for f in range(max_frames):
            # Move
            ma.pos += ma.vel * self.dt
            mb.pos += mb.vel * self.dt

            # Collision
            delta = mb.pos - ma.pos
            dist = float(np.linalg.norm(delta))
            min_d = ma.radius + mb.radius
            if dist < min_d and dist > 1e-6:
                normal = delta / dist
                overlap = min_d - dist
                total_mass = ma.mass + mb.mass
                ma.pos -= normal * overlap * (mb.mass / total_mass)
                mb.pos += normal * overlap * (ma.mass / total_mass)
                v1n = float(np.dot(ma.vel, normal))
                v2n = float(np.dot(mb.vel, normal))
                if v1n - v2n <= 0:
                    new_v1n = (v1n * (ma.mass - mb.mass) + 2 * mb.mass * v2n) / total_mass
                    new_v2n = (v2n * (mb.mass - ma.mass) + 2 * ma.mass * v1n) / total_mass
                    ma.vel += (new_v1n - v1n) * normal
                    mb.vel += (new_v2n - v2n) * normal

            # Soft drag (keeps the arena lively but lets fast collisions decide)
            ma.vel *= 0.992
            mb.vel *= 0.992

            # Check ring exit
            for m in (ma, mb):
                offset_x = m.pos[0] - self.ring_cx
                offset_y = m.pos[1] - self.ring_cy
                d_from_center = math.sqrt(offset_x ** 2 + offset_y ** 2)
                if d_from_center > self.ring_r:
                    m.outside_frames += 1
                else:
                    m.outside_frames = 0

            trajectory.append((ma.pos.copy(), mb.pos.copy()))

            # Decision
            if ma.outside_frames >= 10:
                winner_idx = 1
                decision_frame = f
                break
            if mb.outside_frames >= 10:
                winner_idx = 0
                decision_frame = f
                break

        # If timed out: closer-to-center wins
        if winner_idx is None:
            da = math.hypot(ma.pos[0] - self.ring_cx, ma.pos[1] - self.ring_cy)
            db = math.hypot(mb.pos[0] - self.ring_cx, mb.pos[1] - self.ring_cy)
            winner_idx = 0 if da <= db else 1
            decision_frame = len(trajectory) - 1

        # Hold final state for a few frames so the verdict reads
        hold_frames = int(self.fps * 0.5)
        last = trajectory[-1]
        for _ in range(hold_frames):
            trajectory.append((last[0].copy(), last[1].copy()))

        return MatchResult(
            team_a=team_a, team_b=team_b,
            winner_idx=winner_idx,
            duration_frames=len(trajectory),
            trajectory=trajectory,
            decision_frame=decision_frame,
        )

    # ===== Background =====

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

    # ===== Lookup current match at a global frame =====

    def _match_at(self, frame: int):
        """Return (match_idx, local_frame, in_match) for the given frame."""
        if frame < self.intro_frames:
            return (0, 0, False)
        for k, start in enumerate(self.match_starts):
            m = self.matches[k]
            end = start + m.duration_frames
            if frame < end:
                return (k, frame - start, True)
            if frame < end + self.transition_frames:
                # In transition right after match k
                return (k, m.duration_frames - 1, False)
        # Past everything = payoff
        return (len(self.matches) - 1, self.matches[-1].duration_frames - 1, False)

    def _round_label(self, match_idx: int) -> tuple[str, int, int]:
        """Return (round_name, match_in_round, total_in_round)."""
        for r in range(len(self.round_names) - 1, -1, -1):
            start = self.round_starts[r]
            count = self.round_match_counts[r]
            if match_idx >= start and match_idx < start + count:
                return (self.round_names[r], match_idx - start + 1, count)
        return (self.round_names[0], 1, self.round_match_counts[0])

    # ===== Drawing helpers =====

    def _draw_marble(self, draw, x, y, r, color, code, label_color="white"):
        light = tuple(min(255, int(c * 1.5 + 60)) for c in color)
        dark = tuple(int(c * 0.55) for c in color)
        # Shadow
        draw.ellipse([x - r * 0.95, y + r * 0.55, x + r * 0.95, y + r * 1.05],
                     fill=(0, 0, 0, 140))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=dark)
        for k in range(int(r), 0, -2):
            tt = 1 - (k / r)
            blend = _lerp_color(dark, color, tt)
            draw.ellipse([x - k, y - k, x + k, y + k], fill=blend)
        hl = r * 0.42
        draw.ellipse([x - hl - r * 0.22, y - hl - r * 0.22,
                      x + hl - r * 0.22, y + hl - r * 0.22], fill=light)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     outline=(255, 255, 255, 200), width=3)
        # Code label centered
        bbox = draw.textbbox((0, 0), code, font=self.font_code_match)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x - tw / 2, y - th / 2 - 2),
                  code, font=self.font_code_match,
                  fill=label_color, stroke_width=2, stroke_fill="black")

    def _draw_ring(self, draw, frame_in_match: int, decision_frame: int):
        # Pulsing arena boundary — green normal, gold flash near decision
        cx, cy = self.ring_cx, self.ring_cy
        # Outer halo
        for offset, alpha in [(14, 35), (7, 80)]:
            draw.ellipse([cx - self.ring_r - offset, cy - self.ring_r - offset,
                          cx + self.ring_r + offset, cy + self.ring_r + offset],
                         outline=(*self.brand_green, alpha), width=2)
        # Main ring
        ring_color = (*self.brand_green, 220)
        # Flash gold for 6 frames after decision
        if 0 <= frame_in_match - decision_frame < 6:
            ring_color = (*self.brand_gold, 240)
        draw.ellipse([cx - self.ring_r, cy - self.ring_r,
                      cx + self.ring_r, cy + self.ring_r],
                     outline=ring_color, width=4)

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

    def _draw_round_label(self, img, match_idx: int):
        draw = ImageDraw.Draw(img, "RGBA")
        rname, mi, total = self._round_label(match_idx)
        long_names = {"R16": "ROUND OF 16", "QF": "QUARTERFINALS", "SF": "SEMIFINALS", "F": "THE FINAL"}
        head = long_names[rname]
        sub = f"MATCH {mi}/{total}" if total > 1 else "WINNER TAKES ALL"

        bbox = draw.textbbox((0, 0), head, font=self.font_round_label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        y_head = 175
        # Banded background
        pad_x, pad_y = 28, 14
        draw.rectangle([(self.w - tw)//2 - pad_x, y_head - pad_y,
                        (self.w + tw)//2 + pad_x, y_head + th + pad_y],
                       fill=(0, 0, 0, 160))
        draw.text(((self.w - tw)//2, y_head), head, font=self.font_round_label,
                  fill="white", stroke_width=3, stroke_fill="black")

        bbox = draw.textbbox((0, 0), sub, font=self.font_match_idx)
        sw = bbox[2] - bbox[0]
        draw.text(((self.w - sw)//2, y_head + th + 24), sub,
                  font=self.font_match_idx,
                  fill=(218, 230, 223, 220))

    def _draw_bracket_pyramid(self, img, match_idx_now: int, in_payoff: bool = False):
        """Compact pyramid below the arena showing survivors at each round.

        Layout (top→bottom):
          row 0: 1 box  (champion)
          row 1: 2 boxes (SF winners → finalists)
          row 2: 4 boxes (QF winners → semifinalists)
          row 3: 8 boxes (R16 winners → quarterfinalists)
          row 4: 16 boxes (R16 starters)
        """
        draw = ImageDraw.Draw(img, "RGBA")
        top_y = 1230
        row_h = 58
        # Widths to fit 16 boxes across 1080 with margins
        margin_x = 30
        usable_w = self.w - 2 * margin_x
        box_h = 38

        # Build survivor lists per round
        r16_codes = [t["code"] for t in self.r16_teams]
        qf_codes = []
        sf_codes = []
        f_codes = []
        champ_code = None

        # Determine how many matches in each round are "completed enough to show"
        # A match is "complete" once frame is at or past its decision frame.
        # match_idx_now is the current match index (0-indexed); matches 0..match_idx_now-1
        # have been decided, the current one may be mid-flight.
        for k in range(self.round_starts[1]):  # R16 matches 0..7
            if k <= match_idx_now:
                m = self.matches[k]
                if k < match_idx_now or self._is_past_decision(k, match_idx_now):
                    qf_codes.append(m.team_a["code"] if m.winner_idx == 0 else m.team_b["code"])
        for k in range(self.round_starts[1], self.round_starts[2]):  # QF
            if k <= match_idx_now:
                m = self.matches[k]
                if k < match_idx_now or self._is_past_decision(k, match_idx_now):
                    sf_codes.append(m.team_a["code"] if m.winner_idx == 0 else m.team_b["code"])
        for k in range(self.round_starts[2], self.round_starts[3]):  # SF
            if k <= match_idx_now:
                m = self.matches[k]
                if k < match_idx_now or self._is_past_decision(k, match_idx_now):
                    f_codes.append(m.team_a["code"] if m.winner_idx == 0 else m.team_b["code"])
        final_idx = self.round_starts[3]
        if in_payoff:
            champ_code = self.champion["code"]
        elif final_idx <= match_idx_now:
            m = self.matches[final_idx]
            if final_idx < match_idx_now or self._is_past_decision(final_idx, match_idx_now):
                champ_code = m.team_a["code"] if m.winner_idx == 0 else m.team_b["code"]

        rows = [
            (1, [champ_code] if champ_code else []),
            (2, f_codes),
            (4, sf_codes),
            (8, qf_codes),
            (16, r16_codes),
        ]

        for ri, (slot_count, codes) in enumerate(rows):
            y = top_y + ri * row_h
            slot_w = usable_w / slot_count
            for s in range(slot_count):
                x0 = margin_x + s * slot_w + 3
                x1 = margin_x + (s + 1) * slot_w - 3
                # Determine fill: empty / present / champion-gold
                is_champion_slot = (ri == 0 and codes)
                code = codes[s] if s < len(codes) else None
                if code is None:
                    fill = (255, 255, 255, 20)
                    outline = (255, 255, 255, 60)
                    text_color = (255, 255, 255, 80)
                else:
                    if is_champion_slot:
                        fill = (*self.brand_gold, 230)
                        outline = (*self.brand_gold, 255)
                        text_color = (0, 0, 0)
                    else:
                        fill = (*self.brand_green, 130)
                        outline = (*self.brand_green, 220)
                        text_color = (255, 255, 255)
                draw.rounded_rectangle([x0, y, x1, y + box_h], radius=6,
                                       fill=fill, outline=outline, width=1)
                if code:
                    bbox = draw.textbbox((0, 0), code, font=self.font_bracket_code)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    draw.text((x0 + (x1 - x0 - tw) / 2, y + (box_h - th) / 2 - 1),
                              code, font=self.font_bracket_code, fill=text_color)

    def _is_past_decision(self, match_idx: int, current_match_idx: int) -> bool:
        # Always true if current_match > match_idx (already decided + transitioned)
        return current_match_idx > match_idx

    def _draw_payoff(self, img, frame: int):
        if frame < self.winner_frame:
            return
        fade = min((frame - self.winner_frame) / 18, 1.0)
        scrim = Image.new("RGBA", img.size, (0, 0, 0, int(220 * fade)))
        img.paste(scrim, (0, 0), scrim)

        draw = ImageDraw.Draw(img, "RGBA")
        cy = self.h // 2

        eb = "PHYSICS PICKED YOUR CHAMPION"
        bbox = draw.textbbox((0, 0), eb, font=self.font_payoff_eyebrow)
        tw = bbox[2] - bbox[0]
        draw.text(((self.w - tw) // 2, cy - 280), eb,
                  font=self.font_payoff_eyebrow, fill=(218, 230, 223, 230))

        text = self.champion["code"]
        bbox = draw.textbbox((0, 0), text, font=self.font_payoff_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((self.w - tw) // 2, cy - th // 2),
                  text, font=self.font_payoff_main,
                  fill=self.brand_gold,
                  stroke_width=6, stroke_fill="black")

        sub = f"ELO {self.champion['elo']}"
        bbox = draw.textbbox((0, 0), sub, font=self.font_payoff_sub)
        sw = bbox[2] - bbox[0]
        draw.text(((self.w - sw) // 2, cy + th // 2 + 30),
                  sub, font=self.font_payoff_sub,
                  fill="white", stroke_width=2, stroke_fill="black")

    # ===== Frame =====

    def frame(self, i: int) -> Image.Image:
        img = self.bg_cache.copy()
        draw = ImageDraw.Draw(img, "RGBA")

        match_idx, local_f, _ = self._match_at(i)
        m = self.matches[match_idx]

        # Ring + marbles (skip during pre-intro)
        if i >= self.intro_frames:
            self._draw_ring(draw, local_f, m.decision_frame)
            # Get marble positions at this local frame
            local_f = max(0, min(local_f, len(m.trajectory) - 1))
            pos_a, pos_b = m.trajectory[local_f]
            # Determine radius from elo
            ra = self.min_r + m.team_a["elo_t"] * (self.max_r - self.min_r)
            rb = self.min_r + m.team_b["elo_t"] * (self.max_r - self.min_r)
            self._draw_marble(draw, pos_a[0], pos_a[1], ra,
                              _hex(m.team_a["color"]), m.team_a["code"])
            self._draw_marble(draw, pos_b[0], pos_b[1], rb,
                              _hex(m.team_b["color"]), m.team_b["code"])

            # If decision passed, highlight loser with red X (briefly)
            past_decision = local_f - m.decision_frame
            if 2 <= past_decision <= 30:
                loser_idx = 1 - m.winner_idx
                lpos = pos_b if loser_idx == 1 else pos_a
                lr = rb if loser_idx == 1 else ra
                draw.line([lpos[0] - lr * 0.7, lpos[1] - lr * 0.7,
                           lpos[0] + lr * 0.7, lpos[1] + lr * 0.7],
                          fill=(*self.danger, 230), width=6)
                draw.line([lpos[0] - lr * 0.7, lpos[1] + lr * 0.7,
                           lpos[0] + lr * 0.7, lpos[1] - lr * 0.7],
                          fill=(*self.danger, 230), width=6)

        # Chrome
        self._draw_watermark(img)
        self._draw_round_chip(img)
        if i >= self.intro_frames - 5:
            self._draw_round_label(img, match_idx)
        self._draw_bracket_pyramid(img, match_idx, in_payoff=(i >= self.winner_frame))

        # Hook (only during intro)
        if i < int(self.fps * 2.5):
            text = self.hook_text.upper()
            bbox = draw.textbbox((0, 0), text, font=self.font_hook)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            pad_x, pad_y = 28, 14
            y_top = 1530
            draw.rectangle([(self.w - tw)//2 - pad_x, y_top - pad_y,
                            (self.w + tw)//2 + pad_x, y_top + th + pad_y],
                           fill=(0, 0, 0, 180))
            draw.text(((self.w - tw)//2, y_top), text, font=self.font_hook,
                      fill="white", stroke_width=3, stroke_fill="black")

        # CTA
        if i >= int(self.fps * 0.5):
            text = self.cta_text.upper()
            bbox = draw.textbbox((0, 0), text, font=self.font_cta)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            pad_x, pad_y = 28, 14
            y_top = int(self.h * 0.945)
            draw.rectangle([(self.w - tw)//2 - pad_x, y_top - pad_y,
                            (self.w + tw)//2 + pad_x, y_top + th + pad_y],
                           fill=(0, 0, 0, 180))
            draw.text(((self.w - tw)//2, y_top), text, font=self.font_cta,
                      fill="white", stroke_width=3, stroke_fill="black")

        # Payoff
        self._draw_payoff(img, i)
        return img

    def __iter__(self):
        for i in range(self.num_frames):
            yield self.frame(i)
