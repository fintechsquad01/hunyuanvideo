"""ElevenLabs narration generation.

Requires ELEVENLABS_API_KEY in env. Outputs a WAV at the target path.
If the key isn't set or the call fails, writes a silent WAV of the same
duration so downstream mux still works.

Two narration cues:
  open  → "Every World Cup. Every champion."
  close → "Eight nations. Pick yours."

Voice: a deep cinematic male voice. Defaults to "George" / VOICE_ID below
but can be overridden by env var ELEVENLABS_VOICE_ID.
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
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # "George" — warm, narrative
MODEL_ID = "eleven_multilingual_v2"


CUES = {
    "open": "Every World Cup. Every champion.",
    "close": "Eight nations. Pick yours.",
}


def _silent_wav(out_path: Path, seconds: float) -> Path:
    n = int(seconds * SR)
    pcm = np.zeros(n, dtype=np.int16)
    out_path.parent.mkdir(exist_ok=True, parents=True)
    wavfile.write(out_path, SR, pcm)
    return out_path


def narrate(text: str, out_path: Path, fallback_seconds: float = 2.0) -> Path:
    """Speak `text` via ElevenLabs TTS, write WAV at out_path.

    Falls back to silent WAV if no key / failure.
    """
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print(f"  no ELEVENLABS_API_KEY — silent WAV for: {text!r}")
        return _silent_wav(out_path, fallback_seconds)

    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.75,
            "style": 0.40,
            "use_speaker_boost": True,
        },
        "output_format": "mp3_44100_128",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            mp3_bytes = r.read()
        mp3_path = out_path.with_suffix(".mp3")
        out_path.parent.mkdir(exist_ok=True, parents=True)
        mp3_path.write_bytes(mp3_bytes)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(mp3_path),
             "-ar", str(SR), "-ac", "1",
             str(out_path)],
            check=True,
        )
        return out_path
    except Exception as e:
        print(f"  ElevenLabs failed for {text!r}: {e!r} — silent fallback")
        return _silent_wav(out_path, fallback_seconds)


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[2] / "output" / "wc_champions_narration"
    base.mkdir(exist_ok=True, parents=True)
    for cue, txt in CUES.items():
        narrate(txt, base / f"{cue}.wav", fallback_seconds={"open": 2.0, "close": 2.5}[cue])
        print(f"  {cue}: {(base / f'{cue}.wav').stat().st_size / 1024:.1f} KB")
