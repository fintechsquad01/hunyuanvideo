"""ElevenLabs narration helper.

Default voice: "George" — warm, narrative, deep male.
Falls back to a silent WAV when ELEVENLABS_API_KEY is missing.
Returns a 44.1 kHz mono WAV at out_path.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path

import numpy as np
from scipy.io import wavfile

SR = 44100
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George
MODEL_ID = "eleven_multilingual_v2"


def _silent_wav(out_path: Path, seconds: float) -> Path:
    n = int(seconds * SR)
    pcm = np.zeros(n, dtype=np.int16)
    out_path.parent.mkdir(exist_ok=True, parents=True)
    wavfile.write(out_path, SR, pcm)
    return out_path


def narrate(text: str, out_path: Path, fallback_seconds: float = 2.0,
            voice_id: str | None = None,
            style: float = 0.4, stability: float = 0.55) -> Path:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print(f"  [tts] no key — silent WAV for {text!r}")
        return _silent_wav(out_path, fallback_seconds)
    vid = voice_id or os.environ.get("ELEVENLABS_VOICE_ID") or DEFAULT_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"
    body = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": 0.75,
            "style": style,
            "use_speaker_boost": True,
        },
        "output_format": "mp3_44100_128",
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"xi-api-key": key, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            mp3 = r.read()
        out_path.parent.mkdir(exist_ok=True, parents=True)
        mp3_path = out_path.with_suffix(".mp3")
        mp3_path.write_bytes(mp3)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(mp3_path), "-ar", str(SR), "-ac", "1", str(out_path)],
            check=True,
        )
        return out_path
    except Exception as e:
        print(f"  [tts] failed for {text!r}: {e!r} — silent")
        return _silent_wav(out_path, fallback_seconds)


def synth_music_bed(out_path: Path, total_s: float, accent_times_s: list[float] | None = None) -> Path:
    """Synthesize a simple music bed: warm pad + per-beat accents.

    accent_times_s: list of seconds where we want a soft melodic hit (e.g.,
    when each datapoint pops onto the screen).
    """
    n = int(total_s * SR)
    buf = np.zeros(n)
    # Pad (suspended fourth chord)
    for f in [196.0, 261.6, 392.0]:  # G3, C4, G4
        t = np.linspace(0, total_s, n, endpoint=False)
        lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.18 * t)
        buf += np.sin(2 * np.pi * f * t) * lfo * 0.08
    # Fade in/out
    fade_n = int(0.4 * SR)
    env = np.concatenate([np.linspace(0, 1, fade_n),
                          np.ones(n - 2 * fade_n),
                          np.linspace(1, 0, fade_n)])
    buf = buf * env

    # Accents: arpeggio notes at given times
    notes = [392.0, 440.0, 493.9, 523.3, 587.3, 659.3, 698.5, 783.9]
    for i, t_s in enumerate(accent_times_s or []):
        start = int(t_s * SR)
        if start >= n - 100:
            continue
        f = notes[i % len(notes)]
        dur_n = min(int(0.45 * SR), n - start)
        tt = np.linspace(0, 0.45, dur_n, endpoint=False)
        sig = (np.sin(2 * np.pi * f * tt)
               + 0.4 * np.sin(2 * np.pi * f * 2 * tt)
               + 0.15 * np.sin(2 * np.pi * f * 3 * tt))
        env_n = np.concatenate([np.linspace(0, 1, int(0.005 * SR)),
                                np.exp(-np.linspace(0, 3.5, dur_n - int(0.005 * SR)))])
        buf[start:start + dur_n] += sig * env_n * 0.18

    peak = float(np.max(np.abs(buf)))
    if peak > 0:
        buf = buf * (0.65 / peak)
    pcm = (buf * 32767).astype(np.int16)
    out_path.parent.mkdir(exist_ok=True, parents=True)
    wavfile.write(out_path, SR, pcm)
    return out_path


def mix_to_wav(out_path: Path, layers: list[tuple[Path, float, float]]) -> Path:
    """Mix multiple WAV layers into one. layers = [(wav_path, start_s, gain), ...].

    Output: 44.1 kHz mono WAV.
    """
    if not layers:
        raise ValueError("mix_to_wav needs at least one layer")
    # Find total duration
    max_end = 0.0
    parsed = []
    for path, start_s, gain in layers:
        sr, data = wavfile.read(path)
        if data.ndim > 1:
            data = data.mean(axis=1).astype(np.int16)
        secs = len(data) / sr
        parsed.append((data.astype(np.float32) / 32767.0, sr, start_s, gain))
        max_end = max(max_end, start_s + secs)
    n_out = int(max_end * SR)
    buf = np.zeros(n_out, dtype=np.float32)
    for data, sr, start_s, gain in parsed:
        if sr != SR:
            # resample crude
            data = np.interp(np.linspace(0, len(data) - 1, int(len(data) * SR / sr)),
                             np.arange(len(data)), data)
        s = int(start_s * SR)
        e = min(n_out, s + len(data))
        buf[s:e] += data[: e - s] * gain
    peak = float(np.max(np.abs(buf)))
    if peak > 1.0:
        buf = buf / peak
    pcm = (buf * 32767).clip(-32767, 32767).astype(np.int16)
    out_path.parent.mkdir(exist_ok=True, parents=True)
    wavfile.write(out_path, SR, pcm)
    return out_path
