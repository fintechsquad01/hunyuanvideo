"""Render the Curaçao gap reveal piece — 14s, 420 frames, audio muxed."""

from __future__ import annotations

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
OUT_DIR = HERE.parent.parent / "output"
FRAMES_DIR = HERE / "_frames"

N_FRAMES = 420       # 14s @ 30fps
FPS = 30
W, H = 1080, 1920
SR = 44100           # audio sample rate

CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Beats — keep in sync with the JS beats in scene.html
BEATS = {
    "s1_text1": 6, "s1_text2": 14, "s1_text3": 22, "s1_out": 60,
    "s2_country": 66, "s2_detail": 78, "s2_out": 120,
    "s3_number": 122, "s3_compare": 144, "s3_out": 210,
    "s4_country": 216, "s4_detail": 228, "s4_out": 270,
    "s5_climb_start": 275, "s5_phase1_end": 305, "s5_lock": 311,
    "s5_phase2_end": 335, "s5_gap_in": 338, "s5_out": 360,
    "s6_headline": 362, "s6_sub": 372, "s6_cta": 380,
}


# ----- AUDIO SYNTHESIS -----

def synth_tone(freq: float, duration_s: float, amp: float = 0.25, attack_s: float = 0.005, decay_s: float = 0.4) -> np.ndarray:
    """One pluck-shaped sine tone with attack + exponential decay."""
    n = int(duration_s * SR)
    t = np.arange(n) / SR
    sine = np.sin(2 * math.pi * freq * t)
    # ADSR-lite envelope: linear attack, exponential decay
    env = np.ones(n, dtype=np.float32)
    attack_n = int(attack_s * SR)
    decay_n = int(decay_s * SR)
    if attack_n > 0:
        env[:attack_n] = np.linspace(0, 1, attack_n)
    if decay_n > 0 and decay_n < n - attack_n:
        decay = np.exp(-np.linspace(0, 4, decay_n))
        env[attack_n:attack_n + decay_n] = decay
        env[attack_n + decay_n:] = 0
    return (sine * env * amp).astype(np.float32)


def synth_chord(freqs: list[float], duration_s: float, amp: float = 0.10) -> np.ndarray:
    """A soft sustained chord — ambient pad layer."""
    n = int(duration_s * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    for f in freqs:
        out += np.sin(2 * math.pi * f * t) / len(freqs)
    # Soft attack + release
    attack = int(0.3 * SR)
    release = int(0.5 * SR)
    env = np.ones(n, dtype=np.float32)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    return (out * env * amp).astype(np.float32)


def synth_kick(duration_s: float = 0.4, amp: float = 0.5) -> np.ndarray:
    """Punchy low-frequency kick — for the beat drop on shot 6."""
    n = int(duration_s * SR)
    t = np.arange(n) / SR
    freq = 60 + 200 * np.exp(-t * 30)
    phase = np.cumsum(2 * math.pi * freq / SR)
    sine = np.sin(phase)
    env = np.exp(-t * 5)
    return (sine * env * amp).astype(np.float32)


def build_audio() -> np.ndarray:
    """Assemble the full 14s soundtrack from sine-synth events.

    All sounds are produced from first principles — zero copyrighted audio.
    """
    total_samples = int(N_FRAMES / FPS * SR)
    audio = np.zeros(total_samples, dtype=np.float32)

    def stamp(samples: np.ndarray, frame: int):
        start = int(frame / FPS * SR)
        end = min(start + len(samples), total_samples)
        if end <= start:
            return
        audio[start:end] += samples[: end - start]

    # ---- Ambient pad bed: starts at shot 1, fades out before shot 6 ----
    bed_duration_s = (BEATS["s5_out"] - 0) / FPS
    pad_freqs_minor = [220, 277.2, 329.6]  # A3 + C#4 + E4 — A minor-ish
    pad = synth_chord(pad_freqs_minor, bed_duration_s, amp=0.08)
    stamp(pad, 0)

    # ---- Shot 1: hook ticks ----
    stamp(synth_tone(880, 0.15, amp=0.20), BEATS["s1_text1"])    # "WHAT IF" — high tick
    stamp(synth_tone(659, 0.18, amp=0.15), BEATS["s1_text2"])    # second line
    stamp(synth_tone(523, 0.22, amp=0.15), BEATS["s1_text3"])    # third line

    # ---- Shot 2: subject reveal — three-note tick on CURAÇAO syllables ----
    stamp(synth_tone(523, 0.20, amp=0.22), BEATS["s2_country"])      # CU
    stamp(synth_tone(587, 0.18, amp=0.20), BEATS["s2_country"] + 4)  # RA
    stamp(synth_tone(659, 0.20, amp=0.22), BEATS["s2_country"] + 8)  # ÇAO

    # ---- Shot 3: population reveal — bass hit + sparkle ----
    stamp(synth_tone(110, 0.6, amp=0.35, decay_s=0.6), BEATS["s3_number"])  # deep A2
    stamp(synth_tone(1320, 0.3, amp=0.10), BEATS["s3_compare"])             # high sparkle
    stamp(synth_tone(1480, 0.3, amp=0.08), BEATS["s3_compare"] + 6)

    # ---- Shot 4: opponent intro — darker descending ticks ----
    stamp(synth_tone(440, 0.20, amp=0.22), BEATS["s4_country"])
    stamp(synth_tone(370, 0.20, amp=0.22), BEATS["s4_country"] + 5)
    stamp(synth_tone(330, 0.30, amp=0.25, decay_s=0.5), BEATS["s4_detail"])

    # ---- Shot 5: gap reveal — rising arpeggio synced to counter climb ----
    arp_freqs = [262, 330, 392, 523, 659, 784, 988, 1175]  # C-major rising
    climb_frames = list(range(BEATS["s5_climb_start"], BEATS["s5_phase2_end"], 5))
    for i, f in enumerate(climb_frames[:len(arp_freqs)]):
        stamp(synth_tone(arp_freqs[i], 0.25, amp=0.18), f)
    # Lock thunk on Curaçao
    stamp(synth_tone(146, 0.35, amp=0.4, decay_s=0.5), BEATS["s5_lock"])
    # Beat drop on gap reveal
    stamp(synth_kick(0.5, amp=0.55), BEATS["s5_gap_in"])
    stamp(synth_chord([130, 196, 261], 0.8, amp=0.20), BEATS["s5_gap_in"])

    # ---- Shot 6: payoff — sustained triumphant chord ----
    final_chord = synth_chord([261, 329, 392, 523], 1.6, amp=0.18)  # C major
    stamp(final_chord, BEATS["s6_headline"])
    stamp(synth_kick(0.4, amp=0.4), BEATS["s6_cta"])

    # Soft limiter
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


# ----- VIDEO RENDERING -----

def render_frames():
    FRAMES_DIR.mkdir(exist_ok=True, parents=True)
    for f in FRAMES_DIR.glob("*.png"):
        f.unlink()

    t0 = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        ctx = browser.new_context(viewport={"width": W, "height": H})
        page = ctx.new_page()
        page.goto(f"file://{HTML}")
        page.wait_for_function("document.fonts.status === 'loaded'", timeout=10000)
        page.wait_for_timeout(300)
        for i in range(N_FRAMES):
            page.evaluate(f"window.renderFrame({i})")
            page.screenshot(path=str(FRAMES_DIR / f"frame_{i:04d}.png"), full_page=False)
            if i % 30 == 0:
                print(f"  frame {i}/{N_FRAMES}", flush=True)
        browser.close()
    print(f"\nframes rendered in {time.time() - t0:.1f}s")


def mux(silent_video: Path, audio_wav: Path, out_path: Path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg, "-y",
        "-i", str(silent_video),
        "-i", str(audio_wav),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    t_start = time.time()

    # 1. Render frames
    print(">>> rendering frames")
    render_frames()

    # 2. Stitch frames into silent MP4
    print(">>> stitching silent video")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    silent_mp4 = HERE / "_silent.mp4"
    subprocess.run([
        ffmpeg, "-y",
        "-framerate", str(FPS),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        str(silent_mp4),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Build audio
    print(">>> synthesizing audio")
    audio = build_audio()
    wav_path = HERE / "_audio.wav"
    write_wav(wav_path, audio)

    # 4. Mux
    print(">>> muxing audio + video")
    final_path = OUT_DIR / "curacao_gap_reveal.mp4"
    mux(silent_mp4, wav_path, final_path)

    print(f"\nDONE in {time.time() - t_start:.1f}s")
    print(f"output: {final_path}")


if __name__ == "__main__":
    main()
