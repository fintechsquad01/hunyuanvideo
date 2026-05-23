"""Render WC2026 · The Risers — 10-marble Elo trajectory race over 8 years.

Pure data-driven motion. Each marble's path traces the team's REAL Elo
monthly history from 2018-01-31 to 2026-05-23 (101 monthly snapshots
from soccer_national_team_elo). No rigging — the lines cross where they
actually crossed.

Audio: ambient pad bed, tick on each "year crossed" milestone, beat
drop on the payoff reveal. All synth-generated.
"""

from __future__ import annotations

import json
import math
import subprocess
import time
import wave
from pathlib import Path

import numpy as np
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
HTML = HERE / "scene.html"
TRAJ = HERE / "trajectories.json"
OUT_DIR = HERE.parent.parent / "output"

N_FRAMES = 540       # 18s @ 30fps
FPS = 30
W, H = 1080, 1920
SR = 44100
CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def synth_tone(freq, dur_s, amp=0.25, attack_s=0.005, decay_s=0.4):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sine = np.sin(2 * math.pi * freq * t)
    env = np.ones(n, dtype=np.float32)
    a = int(attack_s * SR); d = int(decay_s * SR)
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
    a = int(0.3 * SR); r = int(0.5 * SR)
    env = np.ones(n, dtype=np.float32)
    env[:a] = np.linspace(0, 1, a); env[-r:] = np.linspace(1, 0, r)
    return (out * env * amp).astype(np.float32)


def synth_kick(dur_s=0.5, amp=0.55):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    freq = 60 + 220 * np.exp(-t * 30)
    phase = np.cumsum(2 * math.pi * freq / SR)
    return (np.sin(phase) * np.exp(-t * 5) * amp).astype(np.float32)


def build_audio():
    total = int(N_FRAMES / FPS * SR)
    audio = np.zeros(total, dtype=np.float32)

    def stamp(s, frame):
        start = int(frame / FPS * SR)
        end = min(start + len(s), total)
        if end > start:
            audio[start:end] += s[:end-start]

    # Ambient pad bed
    bed_dur = (N_FRAMES - 30) / FPS
    pad = synth_chord([110, 165, 220, 277], bed_dur, amp=0.07)
    stamp(pad, 0)

    # Hook stinger at start
    stamp(synth_tone(659, 0.25, amp=0.22), 6)

    # Tick every "year" crossed during race (~52 frames per year for 8 years)
    # Race frames 30 → 450 = 420 frames over 8 years = ~52 frames/year
    for k in range(9):
        f = 30 + k * 52
        if f < 450:
            stamp(synth_tone(880 + k * 30, 0.10, amp=0.10), f)

    # Building tension chord every ~120 frames
    for f in [150, 280, 400]:
        stamp(synth_tone(440, 0.4, amp=0.10, decay_s=0.5), f)

    # Payoff
    stamp(synth_kick(0.6, amp=0.6), 460)
    stamp(synth_chord([262, 330, 392, 523], 2.0, amp=0.22), 460)
    stamp(synth_tone(523, 0.4, amp=0.18), 490)
    stamp(synth_kick(0.4, amp=0.45), 520)

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
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    frames_dir = HERE / "_frames"
    frames_dir.mkdir(exist_ok=True)
    for f in frames_dir.glob("*.png"):
        f.unlink()

    # Load trajectories
    trajectories = json.loads(TRAJ.read_text())
    print(f">>> loaded {len(trajectories)} team trajectories")

    print(">>> rendering frames")
    t0 = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        ctx = browser.new_context(viewport={"width": W, "height": H})
        page = ctx.new_page()
        page.goto(f"file://{HTML}")
        page.wait_for_function("document.fonts.status === 'loaded'", timeout=10000)
        # Inject trajectories + boot
        page.evaluate(f"window.TRAJECTORIES = {json.dumps(trajectories)};")
        page.evaluate("window.boot();")
        page.wait_for_timeout(300)
        for i in range(N_FRAMES):
            page.evaluate(f"window.renderFrame({i})")
            page.screenshot(path=str(frames_dir / f"frame_{i:04d}.png"), full_page=False)
            if i % 40 == 0:
                print(f"  frame {i}/{N_FRAMES}", flush=True)
        browser.close()
    print(f"frames done in {time.time() - t0:.1f}s")

    print(">>> stitching video")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    silent = HERE / "_silent.mp4"
    subprocess.run([
        ffmpeg, "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        str(silent),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(">>> audio")
    audio = build_audio()
    wav = HERE / "_audio.wav"
    write_wav(wav, audio)

    print(">>> muxing")
    out = OUT_DIR / "wc_continents.mp4"
    subprocess.run([
        ffmpeg, "-y", "-i", str(silent), "-i", str(wav),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"\nDONE — {out}")


if __name__ == "__main__":
    main()
