"""Render the Curaçao battle-royale piece.

48 country marbles in a shrinking arena. One survives — Curaçao.
Pure physics motion (no charts, no static cards), brand chrome via
the engine's own overlay layer.

Audio is synthesized in pure Python (sine oscillators) so the piece
ships with zero copyrighted material:

- ambient pad bed throughout
- soft "tick" on each elimination
- bigger "thud" when alive count hits milestones (24, 12, 6, 3, 2)
- final beat-drop chord on the payoff
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import time
import wave
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "world-cup-loops"))

from wc_engines.battle_royale import BattleRoyaleEngine  # noqa: E402

CHROMIUM = None  # not needed — pure Python render
SR = 44100


def synth_tone(freq, dur_s, amp=0.25, attack_s=0.005, decay_s=0.4):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sine = np.sin(2 * math.pi * freq * t)
    env = np.ones(n, dtype=np.float32)
    attack_n = int(attack_s * SR)
    decay_n = int(decay_s * SR)
    if attack_n:
        env[:attack_n] = np.linspace(0, 1, attack_n)
    if decay_n > 0 and decay_n < n - attack_n:
        decay = np.exp(-np.linspace(0, 4, decay_n))
        env[attack_n:attack_n + decay_n] = decay
        env[attack_n + decay_n:] = 0
    return (sine * env * amp).astype(np.float32)


def synth_chord(freqs, dur_s, amp=0.10):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    for f in freqs:
        out += np.sin(2 * math.pi * f * t) / len(freqs)
    attack = int(0.3 * SR)
    release = int(0.5 * SR)
    env = np.ones(n, dtype=np.float32)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    return (out * env * amp).astype(np.float32)


def synth_kick(dur_s=0.5, amp=0.55):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    freq = 60 + 220 * np.exp(-t * 30)
    phase = np.cumsum(2 * math.pi * freq / SR)
    sine = np.sin(phase)
    env = np.exp(-t * 5)
    return (sine * env * amp).astype(np.float32)


def synth_tick(freq=1200, dur_s=0.12, amp=0.18):
    return synth_tone(freq, dur_s, amp=amp, attack_s=0.001, decay_s=0.10)


def build_audio(engine: BattleRoyaleEngine) -> np.ndarray:
    total_samples = int(engine.num_frames / engine.fps * SR)
    audio = np.zeros(total_samples, dtype=np.float32)

    def stamp(samples, frame):
        start = int(frame / engine.fps * SR)
        end = min(start + len(samples), total_samples)
        if end <= start:
            return
        audio[start:end] += samples[: end - start]

    # Ambient pad bed (whole piece minus payoff)
    bed_dur = (engine.payoff_frame - 5) / engine.fps
    pad = synth_chord([110, 165, 220, 277], bed_dur, amp=0.08)
    stamp(pad, 0)

    # Hook ticks
    stamp(synth_tone(659, 0.20, amp=0.22), 6)
    stamp(synth_tone(523, 0.20, amp=0.18), 18)
    stamp(synth_tone(440, 0.24, amp=0.16), 30)

    # Per-elimination ticks
    n_total = len(engine.elimination_frames)
    for k, f in enumerate(engine.elimination_frames):
        # Pitch rises slightly with each elimination for tension
        base_pitch = 800 + (k / max(n_total - 1, 1)) * 600
        amp = 0.12 + (k / max(n_total - 1, 1)) * 0.10
        stamp(synth_tick(freq=base_pitch, dur_s=0.10, amp=amp), f)

    # Milestone thuds when alive count hits 24, 12, 6, 3, 2
    milestones = [24, 12, 6, 3, 2]
    n_marbles = len(engine.marbles)
    sorted_elims = sorted(engine.elimination_frames)
    for milestone in milestones:
        # eliminations needed to reach this milestone
        elim_index = n_marbles - milestone
        if 0 <= elim_index - 1 < len(sorted_elims):
            f = sorted_elims[elim_index - 1]
            stamp(synth_tone(180, 0.45, amp=0.32, decay_s=0.55), f)

    # Payoff beat drop
    stamp(synth_kick(0.6, amp=0.6), engine.payoff_frame)
    stamp(synth_chord([262, 330, 392, 523], 1.8, amp=0.20), engine.payoff_frame)
    stamp(synth_tone(523, 0.4, amp=0.20), engine.payoff_frame + 30)
    stamp(synth_kick(0.4, amp=0.5), engine.payoff_frame + 60)

    peak = float(np.max(np.abs(audio)))
    if peak > 0.95:
        audio *= 0.95 / peak
    return audio


def write_wav(path: Path, audio: np.ndarray):
    i16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(i16.tobytes())


def main():
    cfg = json.loads((HERE / "config.json").read_text())
    out_dir = HERE.parent.parent / "output"
    out_dir.mkdir(exist_ok=True, parents=True)

    print(">>> initializing engine")
    engine = BattleRoyaleEngine(cfg)

    print(">>> rendering frames (this is the slow part)")
    silent_path = HERE / "_silent.mp4"
    writer = imageio.get_writer(
        silent_path,
        fps=cfg["fps"],
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=1,
    )
    t0 = time.time()
    try:
        for i, img in enumerate(engine):
            writer.append_data(np.array(img))
            if i % 60 == 0:
                print(f"  frame {i}/{engine.num_frames}", flush=True)
    finally:
        writer.close()
    print(f"frames rendered in {time.time() - t0:.1f}s")

    print(">>> synthesizing audio")
    audio = build_audio(engine)
    wav_path = HERE / "_audio.wav"
    write_wav(wav_path, audio)

    print(">>> muxing audio + video")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    final_path = out_dir / "curacao_battle_royale.mp4"
    subprocess.run([
        ffmpeg, "-y",
        "-i", str(silent_path),
        "-i", str(wav_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_path),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"\nDONE — {final_path}")


if __name__ == "__main__":
    main()
