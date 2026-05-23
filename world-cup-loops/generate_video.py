"""CLI: render a World Cup content video.

Reuses engines from ../zen-loops. Configs can either be standard zen-loops
configs OR a tournament-aware config that references teams.json by code:

    {
      "id": "bracket_plinko_r32",
      "archetype": "marble_drop",
      "team_codes": ["ESP", "FRA", "ENG", "BRA", ...],
      ...
    }

If `team_codes` is present, labels and palette are pulled from teams.json.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent
ZEN_LOOPS = REPO_ROOT.parent / "zen-loops"
sys.path.insert(0, str(ZEN_LOOPS))

from engines.audio_reactive import collision_audio  # noqa: E402
from engines.python_numpy.bouncing_spheres import BouncingSpheresEngine  # noqa: E402
from engines.python_numpy.marble_drop import MarbleDropEngine  # noqa: E402
from engines.python_numpy.ring_expansion import RingExpansionEngine  # noqa: E402
from overlays.text_overlay import apply_overlay  # noqa: E402

ENGINES = {
    "bouncing_spheres": BouncingSpheresEngine,
    "marble_drop": MarbleDropEngine,
    "ring_expansion": RingExpansionEngine,
}


def _load_teams() -> dict:
    data = json.loads((REPO_ROOT / "data" / "teams.json").read_text())
    return {t["code"]: t for t in data["teams"]}


def _resolve_tournament_fields(cfg: dict):
    """If cfg has team_codes, materialize labels and palette from teams.json."""
    team_codes = cfg.get("team_codes")
    if not team_codes:
        return cfg
    teams = _load_teams()
    cfg["labels"] = []
    cfg["palette"] = []
    for code in team_codes:
        team = teams.get(code)
        if team is None:
            raise SystemExit(f"unknown team code: {code}")
        cfg["labels"].append(team["code"])
        cfg["palette"].append(team["color"])
    return cfg


def _mux_audio(video_path: Path, audio_path: Path, out_path: Path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def render(cfg_path: Path) -> Path:
    cfg = json.loads(cfg_path.read_text())
    cfg = _resolve_tournament_fields(cfg)

    archetype = cfg["archetype"]
    if archetype not in ENGINES:
        raise SystemExit(f"unknown archetype: {archetype}")

    engine = ENGINES[archetype](cfg)
    overlay = cfg.get("overlay") or {}
    hook = overlay.get("hook_text")
    cta = overlay.get("cta_text")

    out_dir = REPO_ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    final_path = out_dir / f"{cfg['id']}.mp4"

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        silent_path = td_path / "silent.mp4"

        writer = imageio.get_writer(
            silent_path,
            fps=cfg["fps"],
            codec="libx264",
            pixelformat="yuv420p",
            macro_block_size=1,
        )
        try:
            for img in engine:
                img = apply_overlay(img, hook, cta)
                writer.append_data(np.array(img))
        finally:
            writer.close()

        collision_frames = getattr(engine, "collision_frames", None)
        melody_name = getattr(engine, "melody_name", None) or cfg.get("melody")
        if collision_frames and melody_name:
            melody = collision_audio.MELODIES.get(melody_name)
            if melody is None:
                raise SystemExit(f"unknown melody: {melody_name}")
            audio = collision_audio.synthesize(
                collision_frames=collision_frames,
                melody=melody,
                fps=cfg["fps"],
                total_frames=cfg["duration"] * cfg["fps"],
            )
            wav_path = td_path / "track.wav"
            collision_audio.write_wav(wav_path, audio)
            _mux_audio(silent_path, wav_path, final_path)
        else:
            shutil.move(silent_path, final_path)

    return final_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, type=Path)
    args = p.parse_args()
    out = render(args.config)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
