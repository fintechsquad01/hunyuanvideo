"""Render 'How far can [country] go?' explainer for one or more countries.

Usage: python render.py [code1 code2 ...]
Default: renders USA + ESP.
"""

from __future__ import annotations

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

from wc_engines.path_explainer import PathExplainerEngine  # noqa: E402


# Data pulled live from Supabase (sharpflow / soccer_wc_simulation_probs joined
# to soccer_national_teams and latest soccer_national_team_elo) on 2026-05-23.
# n_sims = 10,000 per team.
COUNTRY_DATA = {
    "USA": {
        "code": "USA", "name": "United States", "color": "#3c3b6e",
        "world_rank": 41, "elo": 1721, "confederation": "CONCACAF",
        "manager": "Mauricio Pochettino",
        "probabilities": {"r32": 0.4987, "r16": 0.1184, "qf": 0.0386,
                          "sf": 0.0101, "final": 0.0023, "champ": 0.0004},
    },
    "ESP": {
        "code": "ESP", "name": "Spain", "color": "#aa151b",
        "world_rank": 1, "elo": 2165, "confederation": "UEFA",
        "manager": "Luis de la Fuente",
        "probabilities": {"r32": 0.9867, "r16": 0.9042, "qf": 0.5358,
                          "sf": 0.3424, "final": 0.2461, "champ": 0.1933},
    },
    "ARG": {
        "code": "ARG", "name": "Argentina", "color": "#75aadb",
        "world_rank": 2, "elo": 2113, "confederation": "CONMEBOL",
        "manager": "Lionel Scaloni",
        "probabilities": {"r32": 0.9745, "r16": 0.8686, "qf": 0.4234,
                          "sf": 0.2515, "final": 0.1714, "champ": 0.1267},
    },
    "BRA": {
        "code": "BRA", "name": "Brazil", "color": "#ffd400",
        "world_rank": 5, "elo": 1984, "confederation": "CONMEBOL",
        "manager": "Carlo Ancelotti",
        "probabilities": {"r32": 0.9488, "r16": 0.7458, "qf": 0.4157,
                          "sf": 0.2316, "final": 0.0866, "champ": 0.0522},
    },
    "ENG": {
        "code": "ENG", "name": "England", "color": "#cf142b",
        "world_rank": 4, "elo": 2020, "confederation": "UEFA",
        "manager": "Thomas Tuchel",
        "probabilities": {"r32": 0.9576, "r16": 0.7890, "qf": 0.3942,
                          "sf": 0.1472, "final": 0.0840, "champ": 0.0562},
    },
    "JPN": {
        "code": "JPN", "name": "Japan", "color": "#bc002d",
        "world_rank": 13, "elo": 1904, "confederation": "AFC",
        "manager": "Hajime Moriyasu",
        "probabilities": {"r32": 0.8770, "r16": 0.5516, "qf": 0.3002,
                          "sf": 0.1611, "final": 0.0862, "champ": 0.0272},
    },
    "URY": {
        "code": "URY", "name": "Uruguay", "color": "#5cbfeb",
        "world_rank": 15, "elo": 1892, "confederation": "CONMEBOL",
        "manager": "Marcelo Bielsa",
        "probabilities": {"r32": 0.8986, "r16": 0.5218, "qf": 0.2751,
                          "sf": 0.1431, "final": 0.0742, "champ": 0.0259},
    },
    "MEX": {
        "code": "MEX", "name": "Mexico", "color": "#006847",
        "world_rank": 20, "elo": 1860, "confederation": "CONCACAF",
        "manager": "Javier Aguirre",
        "probabilities": {"r32": 0.9148, "r16": 0.4421, "qf": 0.2162,
                          "sf": 0.1111, "final": 0.0533, "champ": 0.0145},
    },
    "MAR": {
        "code": "MAR", "name": "Morocco", "color": "#c1272d",
        "world_rank": 24, "elo": 1821, "confederation": "CAF",
        "manager": "Mohamed Ouahbi",
        "probabilities": {"r32": 0.8027, "r16": 0.3350, "qf": 0.1476,
                          "sf": 0.0643, "final": 0.0282, "champ": 0.0083},
    },
    "CAN": {
        "code": "CAN", "name": "Canada", "color": "#ff0000",
        "world_rank": 25, "elo": 1784, "confederation": "CONCACAF",
        "manager": "Jesse Marsch",
        "probabilities": {"r32": 0.8881, "r16": 0.3205, "qf": 0.1295,
                          "sf": 0.0525, "final": 0.0194, "champ": 0.0042},
    },
}


SR = 44100


def synth_tone(freq, dur_s, amp=0.22, attack_s=0.005, decay_s=0.3):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sine = np.sin(2 * math.pi * freq * t)
    env = np.ones(n, dtype=np.float32)
    a = int(attack_s * SR)
    d = int(decay_s * SR)
    if a:
        env[:a] = np.linspace(0, 1, a)
    if d > 0 and d < n - a:
        env[a:a + d] = np.exp(-np.linspace(0, 4, d))
        env[a + d:] = 0
    return (sine * env * amp).astype(np.float32)


def synth_chord(freqs, dur_s, amp=0.10):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    for f in freqs:
        out += np.sin(2 * math.pi * f * t) / len(freqs)
    a = int(0.3 * SR)
    r = int(0.5 * SR)
    env = np.ones(n, dtype=np.float32)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] = np.linspace(1, 0, r)
    return (out * env * amp).astype(np.float32)


def synth_kick(dur_s=0.5, amp=0.5):
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    freq = 60 + 220 * np.exp(-t * 30)
    phase = np.cumsum(2 * math.pi * freq / SR)
    return (np.sin(phase) * np.exp(-t * 5) * amp).astype(np.float32)


def build_audio(engine):
    total = int(engine.num_frames / engine.fps * SR)
    audio = np.zeros(total, dtype=np.float32)

    def stamp(s, frame):
        start = int(frame / engine.fps * SR)
        end = min(start + len(s), total)
        if end > start:
            audio[start:end] += s[:end - start]

    # Soft bed
    bed_dur = (engine.t_payoff_in - 5) / engine.fps
    stamp(synth_chord([110, 165, 220, 277], bed_dur, amp=0.05), 0)

    # Hero whoosh
    stamp(synth_tone(660, 0.18, amp=0.15), engine.t_hero_start + 2)

    # Stage reveal tick (rising pitch per stage)
    for s in range(6):
        t_start = engine.t_stage_first + s * engine.t_stage_step
        pitch = 500 + s * 120
        stamp(synth_tone(pitch, 0.12, amp=0.18, attack_s=0.002, decay_s=0.10), t_start)

    # Payoff
    stamp(synth_kick(0.6, amp=0.55), engine.t_payoff_in)
    stamp(synth_chord([262, 330, 392, 523], 1.8, amp=0.22), engine.t_payoff_in)

    peak = float(np.max(np.abs(audio)))
    if peak > 0.95:
        audio *= 0.95 / peak
    return audio


def write_wav(path: Path, audio: np.ndarray):
    i16 = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(i16.tobytes())


def render_one(country_code: str, out_dir: Path):
    if country_code not in COUNTRY_DATA:
        print(f"!! unknown country: {country_code}. available: {list(COUNTRY_DATA)}")
        return None
    data = COUNTRY_DATA[country_code]
    cfg = {
        "resolution": [1080, 1920],
        "fps": 30,
        "duration": 16,
        "country": data,
        "probabilities": data["probabilities"],
        "round_chip": "WC 2026 · YOUR PATH",
    }
    print(f">>> rendering {country_code} ({data['name']}) — {data['probabilities']['champ']*100:.3f}% to win")
    engine = PathExplainerEngine(cfg)

    silent_path = HERE / f"_silent_{country_code}.mp4"
    writer = imageio.get_writer(silent_path, fps=cfg["fps"],
                                 codec="libx264", pixelformat="yuv420p",
                                 macro_block_size=1, quality=8)
    t0 = time.time()
    try:
        for i, img in enumerate(engine):
            writer.append_data(np.array(img))
            if i % 60 == 0:
                print(f"  frame {i}/{engine.num_frames}", flush=True)
    finally:
        writer.close()
    print(f"  frames in {time.time() - t0:.1f}s")

    audio = build_audio(engine)
    wav_path = HERE / f"_audio_{country_code}.wav"
    write_wav(wav_path, audio)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out_path = out_dir / f"wc_path_{country_code}.mp4"
    subprocess.run([
        ffmpeg, "-y", "-i", str(silent_path), "-i", str(wav_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_path),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    silent_path.unlink(missing_ok=True)
    wav_path.unlink(missing_ok=True)
    print(f"  → {out_path}")
    return out_path


def main():
    out_dir = HERE.parent.parent / "output"
    out_dir.mkdir(exist_ok=True, parents=True)
    args = sys.argv[1:] or ["USA", "ESP"]
    for code in args:
        render_one(code, out_dir)


if __name__ == "__main__":
    main()
