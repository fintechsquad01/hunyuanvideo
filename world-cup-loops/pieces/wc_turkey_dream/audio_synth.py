"""Synthesize a Turkish-folk-inspired audio bed for the wc_turkey_dream piece.

Pure numpy + scipy.io.wavfile, no external assets.

Sections (timestamps align to the 12-scene + 2-title cut at ~79s):
  [0-11s]   CALM:    Soft kanun-like arpeggios (additive sine + decay), low volume
  [11-12s]  HIT:     Single deep tom + filtered noise burst (goal moment)
  [12-30s]  RISE:    Layered arpeggios + light darbuka (filtered noise impulses)
  [30-54s]  PEAK:    Full ensemble: arpeggios + darbuka + low drone, swelling
  [54-66s]  WAKE:    Strip back to single low pad + slow ticking clock
  [66-79s]  OUTRO:   Soft warm pad

The bed is intentionally subtle so the two hero scenes (s06, s09) with
native Veo3 audio can punch through.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100


def envelope(length: int, attack: float = 0.01, decay: float = 0.5) -> np.ndarray:
    t = np.linspace(0, 1, length, endpoint=False)
    atk_n = max(1, int(attack * length))
    dec_n = length - atk_n
    env = np.concatenate([
        np.linspace(0, 1, atk_n, endpoint=False),
        np.exp(-np.linspace(0, decay * 8, dec_n)),
    ])
    return env[:length]


def kanun_note(freq: float, dur_s: float, amp: float = 0.3) -> np.ndarray:
    """Plucked-string-like tone via additive sine + exponential decay."""
    n = int(dur_s * SAMPLE_RATE)
    t = np.linspace(0, dur_s, n, endpoint=False)
    # Fundamental + first 4 harmonics, weighted realistically
    tone = (
        1.00 * np.sin(2 * np.pi * freq * t)
        + 0.45 * np.sin(2 * np.pi * freq * 2 * t)
        + 0.25 * np.sin(2 * np.pi * freq * 3 * t)
        + 0.12 * np.sin(2 * np.pi * freq * 4 * t)
        + 0.06 * np.sin(2 * np.pi * freq * 5 * t)
    )
    env = envelope(n, attack=0.005, decay=0.6)
    return tone * env * amp


def darbuka_hit(dur_s: float = 0.18, low: bool = False) -> np.ndarray:
    """Hand-drum thump via low-frequency sine + filtered noise transient."""
    n = int(dur_s * SAMPLE_RATE)
    t = np.linspace(0, dur_s, n, endpoint=False)
    fund_freq = 70 if low else 180
    fund = np.sin(2 * np.pi * fund_freq * t) * np.exp(-t * (8 if low else 15))
    noise = np.random.normal(0, 1, n) * np.exp(-t * 40)
    return (fund * 0.7 + noise * 0.3) * 0.6


def low_drone(freq: float, dur_s: float, amp: float = 0.15) -> np.ndarray:
    n = int(dur_s * SAMPLE_RATE)
    t = np.linspace(0, dur_s, n, endpoint=False)
    # Slow LFO on amplitude for breathing quality
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.15 * t)
    sig = (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.5 * t)) * lfo
    fade = envelope(n, attack=0.05, decay=0.0)  # long sustain
    return sig * fade * amp


def add_into(buf: np.ndarray, sig: np.ndarray, start_s: float) -> None:
    start = int(start_s * SAMPLE_RATE)
    end = min(len(buf), start + len(sig))
    buf[start:end] += sig[: end - start]


def tick(dur_s: float = 0.03) -> np.ndarray:
    n = int(dur_s * SAMPLE_RATE)
    t = np.linspace(0, dur_s, n, endpoint=False)
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 60) * 0.18


# Hicaz makam-inspired pitch set (A, Bb, C#, D, E, F, G, A) for that
# distinctive Turkish/Middle-Eastern flavor. Frequencies in Hz.
HICAZ = [220.00, 233.08, 277.18, 293.66, 329.63, 349.23, 392.00, 440.00]


def synth_bed(total_s: float = 79.0, out_path: Path | None = None) -> Path:
    n_total = int(total_s * SAMPLE_RATE)
    buf = np.zeros(n_total)

    # CALM (0-11s) — sparse low arpeggio
    for i, t in enumerate(np.arange(0.0, 11.0, 1.2)):
        f = HICAZ[i % 4]
        add_into(buf, kanun_note(f, 1.1, amp=0.18), t)

    # HIT (11-12s) — deep tom + noise transient (goal)
    add_into(buf, darbuka_hit(0.6, low=True) * 1.6, 11.0)
    burst_n = int(0.3 * SAMPLE_RATE)
    burst = np.random.normal(0, 1, burst_n) * np.exp(-np.linspace(0, 4, burst_n)) * 0.4
    add_into(buf, burst, 11.2)

    # RISE (12-30s) — arpeggios + light percussion
    for i, t in enumerate(np.arange(12.0, 30.0, 0.6)):
        f = HICAZ[(i * 2) % 8]
        add_into(buf, kanun_note(f, 0.8, amp=0.22), t)
        if i % 2 == 0:
            add_into(buf, darbuka_hit(0.18), t + 0.3)
    add_into(buf, low_drone(110.0, 18.0, amp=0.10), 12.0)

    # PEAK (30-54s) — full ensemble swelling
    add_into(buf, low_drone(110.0, 24.0, amp=0.18), 30.0)
    add_into(buf, low_drone(165.0, 24.0, amp=0.12), 30.0)
    for i, t in enumerate(np.arange(30.0, 54.0, 0.4)):
        f = HICAZ[i % 8]
        add_into(buf, kanun_note(f, 0.55, amp=0.26), t)
        # Darbuka pattern: BOOM-tek-tek-BOOM
        if i % 4 == 0:
            add_into(buf, darbuka_hit(0.2, low=True), t)
        elif i % 4 in (1, 2):
            add_into(buf, darbuka_hit(0.12), t + 0.1)

    # WAKE (54-66s) — strip back to single pad + ticking clock
    add_into(buf, low_drone(110.0, 12.0, amp=0.08), 54.0)
    for tt in np.arange(54.0, 66.0, 1.0):
        add_into(buf, tick(), tt)

    # OUTRO (66-79s) — soft warm pad
    add_into(buf, low_drone(146.83, 13.0, amp=0.14), 66.0)  # D3
    add_into(buf, low_drone(220.00, 13.0, amp=0.10), 66.0)  # A3

    # Normalize to -3 dBFS to leave headroom for the native-audio hero scenes
    peak = np.max(np.abs(buf))
    if peak > 0:
        buf = buf * (0.707 / peak)

    pcm = (buf * 32767).astype(np.int16)

    if out_path is None:
        out_path = Path(__file__).resolve().parents[2] / "output" / "wc_turkey_audio_bed.wav"
    out_path.parent.mkdir(exist_ok=True)
    wavfile.write(out_path, SAMPLE_RATE, pcm)
    return out_path


if __name__ == "__main__":
    p = synth_bed()
    print(f"Wrote {p} ({p.stat().st_size / 1024:.1f} KB)")
