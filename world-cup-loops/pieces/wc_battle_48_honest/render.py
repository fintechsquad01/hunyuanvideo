"""Render the honest WC2026 Battle of the 48.

Same render pipeline as the prior battle_royale piece but uses the
HONEST engine (no rigging). Audio is synced to the actual eliminations
the simulation produced.
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

from wc_engines.battle_royale_honest import BattleRoyaleHonestEngine  # noqa: E402

SR = 44100


def synth_tone(freq, dur_s, amp=0.25, attack_s=0.005, decay_s=0.4):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sine = np.sin(2 * math.pi * freq * t)
    env = np.ones(n, dtype=np.float32)
    a, d = int(attack_s * SR), int(decay_s * SR)
    if a: env[:a] = np.linspace(0, 1, a)
    if d > 0 and d < n - a:
        env[a:a+d] = np.exp(-np.linspace(0, 4, d))
        env[a+d:] = 0
    return (sine * env * amp).astype(np.float32)


def synth_chord(freqs, dur_s, amp=0.10):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    for f in freqs:
        out += np.sin(2 * math.pi * f * t) / len(freqs)
    a, r = int(0.3 * SR), int(0.5 * SR)
    env = np.ones(n, dtype=np.float32)
    env[:a] = np.linspace(0, 1, a); env[-r:] = np.linspace(1, 0, r)
    return (out * env * amp).astype(np.float32)


def synth_kick(dur_s=0.5, amp=0.55):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    freq = 60 + 220 * np.exp(-t * 30)
    phase = np.cumsum(2 * math.pi * freq / SR)
    return (np.sin(phase) * np.exp(-t * 5) * amp).astype(np.float32)


def build_audio(engine, total_frames):
    total_samples = int(total_frames / engine.fps * SR)
    audio = np.zeros(total_samples, dtype=np.float32)

    def stamp(s, frame):
        start = int(frame / engine.fps * SR)
        end = min(start + len(s), total_samples)
        if end > start:
            audio[start:end] += s[:end-start]

    # Ambient pad bed (whole piece minus payoff)
    if engine.winner_frame is not None:
        bed_dur = (engine.winner_frame - 5) / engine.fps
    else:
        bed_dur = (total_frames - 5) / engine.fps
    stamp(synth_chord([110, 165, 220, 277], bed_dur, amp=0.08), 0)

    # Hook ticks
    stamp(synth_tone(659, 0.20, amp=0.22), 6)
    stamp(synth_tone(523, 0.20, amp=0.18), 18)
    stamp(synth_tone(440, 0.20, amp=0.16), 30)

    # Per-elimination tick, rising in pitch
    n_total = len(engine.elimination_frames)
    for k, f in enumerate(engine.elimination_frames):
        base = 700 + (k / max(n_total - 1, 1)) * 700
        amp = 0.10 + (k / max(n_total - 1, 1)) * 0.12
        stamp(synth_tone(base, 0.10, amp=amp, attack_s=0.001, decay_s=0.08), f)

    # Milestone thuds at 24, 12, 6, 3, 2 alive
    n_marbles = len(engine.marbles)
    milestones = [24, 12, 6, 3, 2]
    sorted_elims = sorted(engine.elimination_frames)
    for m in milestones:
        elim_idx = n_marbles - m
        if 0 <= elim_idx - 1 < len(sorted_elims):
            stamp(synth_tone(180, 0.45, amp=0.32, decay_s=0.55), sorted_elims[elim_idx - 1])

    # Winner reveal
    if engine.winner_frame is not None:
        wf = engine.winner_frame
        stamp(synth_kick(0.6, amp=0.6), wf)
        stamp(synth_chord([262, 330, 392, 523], 2.0, amp=0.22), wf)
        stamp(synth_tone(523, 0.4, amp=0.20), wf + 30)
        stamp(synth_kick(0.4, amp=0.5), wf + 60)

    peak = float(np.max(np.abs(audio)))
    if peak > 0.95:
        audio *= 0.95 / peak
    return audio


def write_wav(path, audio):
    i16 = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(i16.tobytes())


def main():
    cfg = json.loads((HERE / "config.json").read_text())
    out_dir = HERE.parent.parent / "output"
    out_dir.mkdir(exist_ok=True, parents=True)

    print(">>> initializing engine (honest)")
    engine = BattleRoyaleHonestEngine(cfg, seed=42)

    print(">>> rendering frames (this is the slow part)")
    silent_path = HERE / "_silent.mp4"
    writer = imageio.get_writer(silent_path, fps=cfg["fps"],
                                 codec="libx264", pixelformat="yuv420p",
                                 macro_block_size=1)
    t0 = time.time()
    try:
        for i, img in enumerate(engine):
            writer.append_data(np.array(img))
            if i % 60 == 0:
                alive = sum(1 for m in engine.marbles if m.eliminated_frame is None)
                print(f"  frame {i}/{engine.num_frames}  alive={alive}", flush=True)
    finally:
        writer.close()
    print(f"frames in {time.time() - t0:.1f}s")
    print(f"  winner: {engine.winner.code if engine.winner else 'NONE'} "
          f"(decided at frame {engine.winner_frame})")
    print(f"  elimination order: {' → '.join(engine.elimination_order[:10])} ...")

    print(">>> synthesizing audio")
    audio = build_audio(engine, engine.num_frames)
    wav = HERE / "_audio.wav"
    write_wav(wav, audio)

    print(">>> muxing")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out = out_dir / "wc_battle_48_honest.mp4"
    subprocess.run([
        ffmpeg, "-y", "-i", str(silent_path), "-i", str(wav),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"\nDONE — {out}")
    print(f"WINNER: {engine.winner.code if engine.winner else 'no clear winner'}")


if __name__ == "__main__":
    main()
