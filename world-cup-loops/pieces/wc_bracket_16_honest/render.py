"""Render WC2026 16-team bracket knockout piece."""

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

from wc_engines.bracket_honest import BracketHonestEngine  # noqa: E402

SR = 44100


def synth_tone(freq, dur_s, amp=0.25, attack_s=0.005, decay_s=0.4):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sine = np.sin(2 * math.pi * freq * t)
    env = np.ones(n, dtype=np.float32)
    a, d = int(attack_s * SR), int(decay_s * SR)
    if a: env[:a] = np.linspace(0, 1, a)
    if d > 0 and d < n - a:
        env[a:a+d] = np.exp(-np.linspace(0, 4, d)); env[a+d:] = 0
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
    total = int(total_frames / engine.fps * SR)
    audio = np.zeros(total, dtype=np.float32)

    def stamp(s, frame):
        start = int(frame / engine.fps * SR)
        end = min(start + len(s), total)
        if end > start:
            audio[start:end] += s[:end-start]

    # Pad bed
    bed_dur = (engine.winner_frame - 5) / engine.fps
    stamp(synth_chord([110, 165, 220, 277], bed_dur, amp=0.06), 0)

    # Hook
    stamp(synth_tone(659, 0.20, amp=0.20), 6)
    stamp(synth_tone(523, 0.20, amp=0.16), 18)

    # Round-up tones at the start of each round (rising pitch by round)
    round_base = [392, 494, 587, 698]  # R16, QF, SF, F base
    for r in range(4):
        if r < len(engine.round_starts):
            match_idx = engine.round_starts[r]
            if match_idx < len(engine.match_starts):
                start_frame = engine.match_starts[match_idx]
                stamp(synth_tone(round_base[r], 0.25, amp=0.18), start_frame - 8)

    # Match decision: clack on each decision frame, pitch rises by round
    for k, f in enumerate(engine.match_decision_frames):
        # Determine round
        if k < engine.round_starts[1]:
            base = 700
        elif k < engine.round_starts[2]:
            base = 850
        elif k < engine.round_starts[3]:
            base = 1000
        else:
            base = 1200
        stamp(synth_tone(base, 0.10, amp=0.18, attack_s=0.001, decay_s=0.09), f)

    # Winner moment
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

    print(">>> init engine (bracket honest)")
    engine = BracketHonestEngine(cfg, seed=7)
    print(f"    total matches: {len(engine.matches)}, duration: {engine.duration:.1f}s")
    print(f"    R16 → QF → SF → F → champion: {engine.champion['code']}")
    for r, name in enumerate(engine.round_names):
        s = engine.round_starts[r]
        c = engine.round_match_counts[r]
        print(f"    {name}:")
        for k in range(s, s + c):
            m = engine.matches[k]
            w = m.team_a["code"] if m.winner_idx == 0 else m.team_b["code"]
            l = m.team_b["code"] if m.winner_idx == 0 else m.team_a["code"]
            print(f"      {m.team_a['code']} v {m.team_b['code']}  →  {w}  (in {m.decision_frame/engine.fps:.2f}s)")

    print(">>> rendering frames")
    silent = HERE / "_silent.mp4"
    writer = imageio.get_writer(silent, fps=cfg["fps"],
                                 codec="libx264", pixelformat="yuv420p",
                                 macro_block_size=1)
    t0 = time.time()
    try:
        for i, img in enumerate(engine):
            writer.append_data(np.array(img))
            if i % 30 == 0:
                print(f"  frame {i}/{engine.num_frames}", flush=True)
    finally:
        writer.close()
    print(f"frames in {time.time() - t0:.1f}s")

    print(">>> audio")
    audio = build_audio(engine, engine.num_frames)
    wav = HERE / "_audio.wav"
    write_wav(wav, audio)

    print(">>> mux")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out = out_dir / "wc_bracket_16_honest.mp4"
    subprocess.run([
        ffmpeg, "-y", "-i", str(silent), "-i", str(wav),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"\nDONE — {out}")
    print(f"CHAMPION: {engine.champion['code']} (Elo {engine.champion['elo']})")


if __name__ == "__main__":
    main()
