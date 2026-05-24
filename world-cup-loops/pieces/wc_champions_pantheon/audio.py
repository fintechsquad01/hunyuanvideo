"""Synthesize the audio bed for wc_champions_pantheon.

Two modes:

  synth_local()      → numpy Ode to Joy + trophy-drop note hits.
                       Always works, no network. ~$0.
  synth_elevenlabs() → ElevenLabs music generation, premium cinematic bed.
                       Needs ELEVENLABS_API_KEY + outbound HTTPS access
                       (use from GitHub Actions, not from this session's env).

Both produce a 14.0-second 44.1 kHz mono WAV at the path provided.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import WINNERS  # noqa: E402

SR = 44100
TOTAL_S = 14.0

# Ode to Joy melody — first phrase, ascending pattern (12-tone equal temp)
# E E F G G F E D C C D E E D D  (using the C-major intervals)
# Mapped to one note per trophy drop (22 drops total).
# We use the ascending Joy intervals on a loop.
ODE_NOTES = ["E4", "E4", "F4", "G4", "G4", "F4", "E4", "D4",
             "C4", "C4", "D4", "E4", "E4", "D4", "D4",
             "E4", "F4", "G4", "G4", "F4", "E4", "D4"]


def _note_hz(name: str) -> float:
    """Convert e.g. 'C4' to Hz. A4 = 440 Hz."""
    pitches = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    p = pitches[name[0]]
    octave = int(name[-1])
    midi = 12 * (octave + 1) + p
    return 440.0 * 2 ** ((midi - 69) / 12)


def _env(n: int, attack: float = 0.005, decay: float = 0.4) -> np.ndarray:
    atk = max(1, int(attack * SR))
    dec = max(1, n - atk)
    return np.concatenate([
        np.linspace(0, 1, atk, endpoint=False),
        np.exp(-np.linspace(0, decay * 8, dec)),
    ])[:n]


def _note(freq: float, dur_s: float, amp: float = 0.3) -> np.ndarray:
    n = int(dur_s * SR)
    t = np.linspace(0, dur_s, n, endpoint=False)
    # Plucked-string-like additive synthesis
    sig = (
        1.00 * np.sin(2 * np.pi * freq * t)
        + 0.50 * np.sin(2 * np.pi * freq * 2 * t)
        + 0.25 * np.sin(2 * np.pi * freq * 3 * t)
        + 0.10 * np.sin(2 * np.pi * freq * 4 * t)
    )
    return sig * _env(n, attack=0.003, decay=0.5) * amp


def _pad_chord(notes: list[str], dur_s: float, amp: float = 0.12) -> np.ndarray:
    n = int(dur_s * SR)
    out = np.zeros(n)
    for nm in notes:
        f = _note_hz(nm)
        t = np.linspace(0, dur_s, n, endpoint=False)
        lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.2 * t)
        sig = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 1.5 * t)
        out += sig * lfo
    env = np.concatenate([
        np.linspace(0, 1, int(0.4 * SR)),
        np.ones(n - int(0.4 * SR) - int(0.6 * SR)),
        np.linspace(1, 0, int(0.6 * SR)),
    ])
    return (out / max(1, len(notes))) * env * amp


def _add_into(buf: np.ndarray, sig: np.ndarray, start_s: float) -> None:
    start = int(start_s * SR)
    end = min(len(buf), start + len(sig))
    buf[start:end] += sig[: end - start]


def _drop_times_s() -> list[float]:
    """Frame indices where each trophy drop starts, in seconds."""
    # Mirrors render.py's _drop_schedule(): 6 drops at 20-frame stride from f=60,
    # then 16 drops at 9.375-frame stride from f=180. fps=30.
    times: list[float] = []
    for idx in range(6):
        times.append((60 + idx * 20) / 30.0)
    for idx in range(16):
        times.append((180 + int(idx * 150 / 16)) / 30.0)
    return times


def synth_local(out_path: Path) -> Path:
    """Numpy-only Ode to Joy bed + per-drop note hits. Always works."""
    n = int(TOTAL_S * SR)
    buf = np.zeros(n)

    # SHOT 1 (0–2s): soft suspended pad
    _add_into(buf, _pad_chord(["C3", "G3", "D4"], 2.0, amp=0.10), 0.0)

    # SHOTS 2–3 (2–11s): per-drop melody notes
    drop_times = _drop_times_s()
    for i, t_drop in enumerate(drop_times):
        nm = ODE_NOTES[i % len(ODE_NOTES)]
        f = _note_hz(nm)
        # Each note ~0.5s long; amp rises slightly through the climb
        amp = 0.28 + 0.12 * (i / max(1, len(drop_times) - 1))
        _add_into(buf, _note(f, 0.55, amp=amp), t_drop)

    # SHOT 4 (11–13s): tonic resolution chord
    _add_into(buf, _pad_chord(["C3", "E3", "G3", "C4"], 2.0, amp=0.18), 11.0)

    # SHOT 5 (13–14s): pad fades into silence
    _add_into(buf, _pad_chord(["C3", "G3"], 1.0, amp=0.08), 13.0)

    # Normalize, leave ~3dB headroom
    peak = float(np.max(np.abs(buf)))
    if peak > 0:
        buf = buf * (0.707 / peak)
    pcm = (buf * 32767).astype(np.int16)

    out_path.parent.mkdir(exist_ok=True, parents=True)
    wavfile.write(out_path, SR, pcm)
    return out_path


def synth_elevenlabs(out_path: Path, prompt: str | None = None) -> Path:
    """ElevenLabs music generation. Needs ELEVENLABS_API_KEY in env.

    Falls back to synth_local() if no key or the request fails. This function
    is intended to run from a GitHub Actions runner where api.elevenlabs.io is
    reachable; from inside this Claude Code session it will 403 at the proxy.
    """
    import urllib.request
    import json

    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print("  no ELEVENLABS_API_KEY — falling back to synth_local")
        return synth_local(out_path)

    prompt = prompt or (
        "14-second cinematic sports retrospective cue. Ode to Joy melody motif, "
        "soft orchestral pad open, ascending plucked strings during the build, "
        "swelling brass and tonic resolution at 11 seconds, reverb tail to silence. "
        "No vocals. No drums. Tempo synced for a trophy-cascade animation."
    )
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/music",
        data=json.dumps({
            "prompt": prompt,
            "music_length_ms": int(TOTAL_S * 1000),
            "output_format": "mp3_44100_128",
        }).encode("utf-8"),
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            mp3_bytes = r.read()
        mp3_path = out_path.with_suffix(".mp3")
        mp3_path.write_bytes(mp3_bytes)
        # Convert to wav for downstream consistency
        import subprocess
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3_path),
             "-ar", str(SR), "-ac", "1", str(out_path)],
            check=True,
        )
        return out_path
    except Exception as e:
        print(f"  ElevenLabs failed ({e!r}) — falling back to synth_local")
        return synth_local(out_path)


if __name__ == "__main__":
    p = Path(__file__).resolve().parents[2] / "output" / "wc_champions_pantheon_audio.wav"
    mode = "elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else "local"
    print(f"Mode: {mode}")
    if mode == "elevenlabs":
        synth_elevenlabs(p)
    else:
        synth_local(p)
    print(f"Wrote {p} ({p.stat().st_size / 1024:.1f} KB)")
