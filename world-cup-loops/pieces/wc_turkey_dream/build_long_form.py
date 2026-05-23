"""Build the wc_turkey_dream long-form video from the 12 generated scenes + 2 title cards.

Run this from a FRESH session that has CloudFront in its outbound allowlist
(the original session that kicked off generation cannot download).

  cd world-cup-loops
  python pieces/wc_turkey_dream/build_long_form.py

Pipeline:
  1. Read job_urls.json
  2. For each pending scene, poll job_display until it completes (or skip if you've pre-populated URLs)
  3. Download each scene MP4 (skip if already on disk)
  4. Render title cards locally (PIL + ffmpeg)
  5. Synthesize the Turkish-folk audio bed locally
  6. Normalize every clip to 768x1344 30fps yuv420p
  7. Hard-cut concatenate intro_title + 12 scenes + outro_title via ffmpeg concat demuxer
  8. Overlay the synth audio bed; keep the native audio from the two hero scenes (s06, s09) ducked-in
  9. Output: output/wc_turkey_dream.mp4
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parents[1] / "output"
RAW_DIR = OUTPUT / "wc_turkey_raw"
NORM_DIR = OUTPUT / "wc_turkey_norm"
OUTPUT.mkdir(exist_ok=True)
RAW_DIR.mkdir(exist_ok=True)
NORM_DIR.mkdir(exist_ok=True)

URLS_FILE = ROOT / "job_urls.json"
FINAL = OUTPUT / "wc_turkey_dream.mp4"

W, H, FPS = 768, 1344, 30

# Final cut order. Scene IDs match keys in job_urls.json["scenes"].
ORDER: list[str] = [
    "t01_title",  # 5s
    "s01_calm", "s02_goal", "s03_galata", "s04_dervish", "s05_cappadocia",
    "s06_bosphorus", "s07b_unity", "s08b_simit", "s07_cats",
    "s08_baklava", "s09_taksim", "s10_wake",
    "t02_outro",  # 6s
]

# Scenes whose native audio should survive in the final mix.
NATIVE_AUDIO_SCENES = {"s06_bosphorus", "s09_taksim"}


def run(cmd: list[str]) -> None:
    """Run subprocess, raising on failure."""
    subprocess.run(cmd, check=True)


def download(url: str, dst: Path) -> None:
    if dst.exists() and dst.stat().st_size > 0:
        return
    print(f"  ↓ {dst.name}")
    with urllib.request.urlopen(url, timeout=120) as r, dst.open("wb") as f:
        shutil.copyfileobj(r, f)


def normalize(src: Path, dst: Path, keep_audio: bool) -> None:
    if dst.exists() and dst.stat().st_size > 0:
        return
    print(f"  ↻ {dst.name}")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(src),
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-level", "4.0",
    ]
    if keep_audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "44100"]
    else:
        cmd += ["-an"]
    cmd.append(str(dst))
    run(cmd)


def fetch_pending_urls() -> dict:
    """Poll the MCP for any pending jobs and update URLs.

    NOTE: this function relies on the MCP `job_display` tool being available to
    Claude when this script is invoked through an MCP-aware harness. When run
    as a standalone Python script there is no MCP; in that mode just pre-fill
    the URLs in job_urls.json and skip polling.
    """
    data = json.loads(URLS_FILE.read_text())
    pending = {sid: s for sid, s in data["scenes"].items() if s.get("status") != "completed"}
    if pending:
        print(f"  ! {len(pending)} scene(s) still pending — pre-fill their URLs in job_urls.json before re-running.")
        for sid in pending:
            print(f"      {sid}: job {data['scenes'][sid].get('job_id')}")
    return data


def build() -> Path:
    print("==> Loading URLs")
    data = fetch_pending_urls()
    scenes = data["scenes"]

    print("==> Rendering title cards locally")
    from render_titles import render_all
    title_paths = render_all()

    print("==> Synthesizing audio bed")
    from audio_synth import synth_bed
    bed_path = synth_bed(total_s=sum_duration(scenes))

    print("==> Downloading scene MP4s")
    raw: dict[str, Path] = {}
    for sid in ORDER:
        if sid.startswith("t"):
            raw[sid] = title_paths[sid]
            continue
        url = scenes[sid].get("url")
        if not url:
            raise SystemExit(f"Missing URL for {sid} — fill it in {URLS_FILE} and re-run")
        dst = RAW_DIR / f"{sid}.mp4"
        download(url, dst)
        raw[sid] = dst

    print("==> Normalizing clips")
    norm: list[Path] = []
    for sid in ORDER:
        dst = NORM_DIR / f"{sid}.mp4"
        normalize(raw[sid], dst, keep_audio=(sid in NATIVE_AUDIO_SCENES))
        norm.append(dst)

    print("==> Concatenating video (hard cuts)")
    list_path = OUTPUT / "wc_turkey_concat.txt"
    list_path.write_text("\n".join(f"file '{p}'" for p in norm) + "\n")
    concat_silent = OUTPUT / "wc_turkey_concat_video.mp4"
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-c", "copy",
        str(concat_silent),
    ])

    print("==> Building final audio mix (synth bed + native hero audio)")
    # Compute cumulative offsets to know when hero scenes start.
    offsets: dict[str, float] = {}
    cur = 0.0
    for sid in ORDER:
        offsets[sid] = cur
        if sid.startswith("t"):
            cur += 5 if sid == "t01_title" else 6
        else:
            cur += scenes[sid].get("duration", 6)

    # Extract native audio from hero scenes, padded with silence to its offset.
    hero_audio_paths: list[Path] = []
    for sid in NATIVE_AUDIO_SCENES:
        offset_ms = int(offsets[sid] * 1000)
        out = OUTPUT / f"wc_turkey_hero_audio_{sid}.m4a"
        run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(raw[sid]),
            "-af", f"adelay={offset_ms}|{offset_ms}",
            "-vn", "-c:a", "aac", "-b:a", "192k",
            str(out),
        ])
        hero_audio_paths.append(out)

    # Mix the bed + hero audios, weighted so the heroes punch through.
    mix_inputs = ["-i", str(bed_path)] + sum([["-i", str(p)] for p in hero_audio_paths], [])
    n_streams = 1 + len(hero_audio_paths)
    weights = " ".join(["0.6"] + ["1.4"] * len(hero_audio_paths))
    final_audio = OUTPUT / "wc_turkey_final_audio.m4a"
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        *mix_inputs,
        "-filter_complex", f"amix=inputs={n_streams}:duration=longest:weights={weights}:normalize=0",
        "-c:a", "aac", "-b:a", "192k",
        str(final_audio),
    ])

    print(f"==> Muxing final video → {FINAL.name}")
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(concat_silent),
        "-i", str(final_audio),
        "-c:v", "copy", "-c:a", "copy",
        "-map", "0:v:0", "-map", "1:a:0",
        "-shortest",
        str(FINAL),
    ])

    print(f"\n✓ {FINAL} ({FINAL.stat().st_size / 1024 / 1024:.1f} MB)")
    return FINAL


def sum_duration(scenes: dict) -> float:
    cur = 0.0
    for sid in ORDER:
        if sid == "t01_title":
            cur += 5
        elif sid == "t02_outro":
            cur += 6
        else:
            cur += scenes[sid].get("duration", 6)
    return cur


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT))
    build()
