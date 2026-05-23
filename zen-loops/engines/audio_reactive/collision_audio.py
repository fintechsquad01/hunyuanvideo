"""Collision-driven audio synthesis.

Given a list of frame indices where collisions occurred and a melody, this
module synthesizes a mono WAV where each collision triggers the next note
in the melody (looping). The WAV can then be muxed into the silent render
with ffmpeg.

Audio is generated with simple sine + exponential-decay envelope so we have
zero external audio-library dependencies. The melody is hard-coded as a
list of note names so users can supply their own without parsing MIDI.

Public-domain default melody: Twinkle Twinkle Little Star. Replace at
will for variants — composing a 12-note loop in any DAW and exporting note
names to MELODIES is the legally-safe alternative to fandom IP audio
discussed in docs/audio-library.md.
"""

from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np

A4 = 440.0
_NOTE_TO_SEMITONE = {
    "C": -9, "C#": -8, "Db": -8,
    "D": -7, "D#": -6, "Eb": -6,
    "E": -5,
    "F": -4, "F#": -3, "Gb": -3,
    "G": -2, "G#": -1, "Ab": -1,
    "A": 0, "A#": 1, "Bb": 1,
    "B": 2,
}


def note_to_freq(note: str) -> float:
    """Convert e.g. 'C4', 'F#5' to Hz."""
    for i, ch in enumerate(note):
        if ch.isdigit():
            pitch, octave = note[:i], int(note[i:])
            break
    else:
        raise ValueError(f"bad note: {note}")
    semitone = _NOTE_TO_SEMITONE[pitch] + (octave - 4) * 12
    return A4 * (2 ** (semitone / 12))


MELODIES: dict[str, list[str]] = {
    "twinkle": [
        "C4", "C4", "G4", "G4", "A4", "A4", "G4",
        "F4", "F4", "E4", "E4", "D4", "D4", "C4",
    ],
    "ode_to_joy": [
        "E4", "E4", "F4", "G4", "G4", "F4", "E4", "D4",
        "C4", "C4", "D4", "E4", "E4", "D4", "D4",
    ],
    "minor_arp": [
        "A3", "C4", "E4", "A4", "E4", "C4",
        "A3", "C4", "F4", "A4", "F4", "C4",
        "A3", "B3", "E4", "G4", "E4", "B3",
    ],
}


def synthesize(
    collision_frames: list[int],
    melody: list[str],
    fps: int,
    total_frames: int,
    sample_rate: int = 44100,
    note_decay_s: float = 0.35,
    amplitude: float = 0.22,
) -> np.ndarray:
    """Build a mono float32 PCM array with one note per collision frame.

    Each note: sine wave at the melody-indexed pitch, multiplied by an
    exponential decay envelope so notes don't sustain past their slot.
    """
    total_samples = int(round(total_frames / fps * sample_rate))
    audio = np.zeros(total_samples, dtype=np.float32)
    if not collision_frames or not melody:
        return audio

    n_decay = int(note_decay_s * sample_rate)
    t = np.arange(n_decay, dtype=np.float32) / sample_rate
    envelope = np.exp(-t * 6.0).astype(np.float32)

    for i, frame_idx in enumerate(collision_frames):
        note = melody[i % len(melody)]
        freq = note_to_freq(note)
        wave_arr = np.sin(2 * math.pi * freq * t, dtype=np.float32) * envelope * amplitude

        start = int(round(frame_idx / fps * sample_rate))
        end = min(start + n_decay, total_samples)
        if end <= start:
            continue
        audio[start:end] += wave_arr[: end - start]

    peak = float(np.max(np.abs(audio)))
    if peak > 0.95:
        audio *= 0.95 / peak
    return audio


def write_wav(path: Path, audio: np.ndarray, sample_rate: int = 44100):
    audio_i16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio_i16.tobytes())
