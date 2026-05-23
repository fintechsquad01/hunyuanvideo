"""Render d3_gap.html frame-by-frame via Playwright.

Loads page ONCE, then evaluates renderFrame(N) per frame and screenshots.
Much faster than goto-per-frame.
"""

import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
HTML = HERE / "d3_gap.html"
N_FRAMES = 110
WIDTH = 1080
HEIGHT = 1920
FPS = 30
CHROMIUM = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'


def main():
    out_dir = HERE / "_d3_frames"
    out_dir.mkdir(exist_ok=True)
    for f in out_dir.glob("*.png"):
        f.unlink()

    t0 = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        ctx = browser.new_context(viewport={"width": WIDTH, "height": HEIGHT})
        page = ctx.new_page()
        page.goto(f"file://{HTML}")
        # Wait for fonts
        page.wait_for_function("document.fonts.status === 'loaded'", timeout=10000)
        page.wait_for_timeout(300)
        for i in range(N_FRAMES):
            page.evaluate(f"window.renderFrame({i})")
            page.screenshot(path=str(out_dir / f"frame_{i:04d}.png"), full_page=False)
            if i % 20 == 0:
                print(f"  frame {i}/{N_FRAMES}", flush=True)
        browser.close()
    t_render = time.time() - t0
    print(f"\nrendered {N_FRAMES} frames in {t_render:.1f}s")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out_mp4 = HERE / "d3_gap.mp4"
    subprocess.run([
        ffmpeg, "-y",
        "-framerate", str(FPS),
        "-i", str(out_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        str(out_mp4),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t_total = time.time() - t0
    print(f"wrote {out_mp4} in {t_total:.1f}s total")


if __name__ == "__main__":
    main()
