"""Manim version of the Curaçao vs Germany gap reveal (Shot 5 of storyboard).

Rewritten to use Text() with ValueTracker (no LaTeX dependency).
"""

from manim import *

BG_TOP = "#0d2818"
BG_BOT = "#020a05"
BRAND_GREEN = "#0f9d58"
BRAND_YELLOW = "#ffd400"
DANGER = "#ff4d4d"
CUR_BLUE = "#0033a0"
GER_RED = "#cf142b"
WHITE = "#ffffff"

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.background_color = BG_BOT


def big_num(value, color=WHITE, size=180):
    return Text(f"{int(value)}", font="Anton", font_size=size, color=color, weight=BOLD)


class CuracaoGap(Scene):
    def construct(self):
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_opacity=1,
            stroke_width=0,
        )
        bg.set_fill(color=[BG_BOT, BG_TOP], opacity=1)
        bg.set_sheen_direction(UP)
        self.add(bg)

        # --- TOP HALF: Curaçao ---
        cur_label = Text("CURAÇAO", font="Anton", font_size=84, color=WHITE, weight=BOLD)
        cur_label.to_edge(UP, buff=1.5)

        cur_flag = Rectangle(width=2.0, height=1.2, fill_color=CUR_BLUE, fill_opacity=1, stroke_width=0)
        cur_flag.next_to(cur_label, DOWN, buff=0.3)

        cur_rank = Text("#90 IN THE WORLD", font="Inter", font_size=36, color=WHITE)
        cur_rank.next_to(cur_flag, DOWN, buff=0.3)

        # --- BOTTOM HALF: Germany ---
        ger_label = Text("GERMANY", font="Anton", font_size=84, color=WHITE, weight=BOLD)
        ger_label.to_edge(DOWN, buff=3.5)

        ger_flag = Rectangle(width=2.0, height=1.2, fill_color=GER_RED, fill_opacity=1, stroke_width=0)
        ger_flag.next_to(ger_label, UP, buff=0.3)

        ger_rank = Text("#11 IN THE WORLD", font="Inter", font_size=36, color=WHITE)
        ger_rank.next_to(ger_flag, UP, buff=0.3)

        divider = Line(
            start=[-config.frame_width / 2, 0, 0],
            end=[config.frame_width / 2, 0, 0],
            color=BRAND_GREEN,
            stroke_width=4,
        )

        # ValueTrackers for animated numbers (no LaTeX)
        cur_val = ValueTracker(0)
        ger_val = ValueTracker(0)

        cur_num = always_redraw(
            lambda: big_num(cur_val.get_value(), color=WHITE).next_to(cur_rank, DOWN, buff=0.8)
        )
        ger_num = always_redraw(
            lambda: big_num(ger_val.get_value(), color=WHITE).next_to(ger_rank, UP, buff=0.8)
        )

        self.play(
            FadeIn(cur_label, shift=DOWN * 0.3),
            FadeIn(cur_flag),
            FadeIn(cur_rank, shift=DOWN * 0.2),
            FadeIn(ger_label, shift=UP * 0.3),
            FadeIn(ger_flag),
            FadeIn(ger_rank, shift=UP * 0.2),
            Create(divider),
            run_time=0.5,
        )

        self.add(cur_num, ger_num)

        # Phase 1: both climb together to 1436
        self.play(
            cur_val.animate.set_value(1436),
            ger_val.animate.set_value(1436),
            run_time=1.0,
            rate_func=rate_functions.smooth,
        )

        # Hold beat — CUR locks in yellow (favorite color of the underdog moment)
        cur_locked = big_num(1436, color=BRAND_YELLOW).next_to(cur_rank, DOWN, buff=0.8)
        self.remove(cur_num)
        self.add(cur_locked)
        self.wait(0.2)

        # Phase 2: only Germany continues
        self.play(
            ger_val.animate.set_value(1923),
            run_time=0.9,
            rate_func=rate_functions.smooth,
        )

        # Color the final Germany value danger-red
        ger_locked = big_num(1923, color=DANGER).next_to(ger_rank, UP, buff=0.8)
        self.remove(ger_num)
        self.add(ger_locked)

        # Reveal the gap value center-stage
        gap_label_top = Text("THE GAP", font="Anton", font_size=42, color=WHITE, weight=BOLD)
        gap_label_top.move_to([0, 0.8, 0])

        gap_value = Text("+487", font="Anton", font_size=240, color=DANGER, weight=BOLD)
        gap_value.move_to([0, -0.3, 0])

        gap_label_bot = Text(
            "BIGGEST GAP IN WC HISTORY",
            font="Anton",
            font_size=38,
            color=WHITE,
            weight=BOLD,
        )
        gap_label_bot.move_to([0, -1.8, 0])

        # Black scrim to focus attention
        scrim = Rectangle(
            width=config.frame_width,
            height=2.5,
            fill_color="#000000",
            fill_opacity=0.78,
            stroke_width=0,
        )
        scrim.move_to([0, -0.3, 0])

        self.play(
            FadeIn(scrim),
            FadeIn(gap_label_top, shift=DOWN * 0.3),
            FadeIn(gap_value, scale=1.15),
            FadeIn(gap_label_bot, shift=UP * 0.3),
            run_time=0.5,
        )
        self.wait(0.7)
