"""Resume the hybrid pipeline in a fresh session — pulls Veo openers,
composites with path explainers, ships the 22s hybrid videos.

Each entry maps a country code to its Veo job ID. The script:
  1. Calls the MCP job_display endpoint (via a saved URL or hardcoded mapping)
  2. Downloads the MP4 to /tmp
  3. Runs the existing composite.py pipeline

If cloudfront is still blocked, prints a clear error and exits.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Country → Veo job ID (from the prior session)
JOBS = {
    "ARG": "0cb7c293-9011-47e6-909b-f240994fed1f",
    "ESP": "acac7106-401a-455e-ab24-c03531d27c6b",
    "USA": "d1c99500-911e-4c12-8e86-58a14f08fe83",
    "MAR": "e16ea3e3-baea-45a6-8250-99db3d935cc6",
}

# The Veo URL pattern; the timestamp portion of the filename is captured per
# job by querying job_display. For static fallback, we include the known ARG URL.
KNOWN_URLS = {
    "ARG": "https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_220141_0cb7c293-9011-47e6-909b-f240994fed1f.mp4",
    "USA": "https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_222308_d1c99500-911e-4c12-8e86-58a14f08fe83.mp4",
    "ESP": "https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_222322_acac7106-401a-455e-ab24-c03531d27c6b.mp4",
    "MAR": "https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_222542_e16ea3e3-baea-45a6-8250-99db3d935cc6.mp4",
}


def preflight():
    """Verify cloudfront is reachable before attempting downloads."""
    try:
        result = subprocess.run(
            ["curl", "-sI", "--max-time", "10",
             "https://d8j0ntlcm91z4.cloudfront.net/"],
            capture_output=True, text=True, timeout=15
        )
        if "host_not_allowed" in result.stdout + result.stderr:
            print("!! cloudfront still blocked. Verify the env's allowlist includes")
            print("   d8j0ntlcm91z4.cloudfront.net (or *.cloudfront.net) and that")
            print("   this is a NEW session (the policy doesn't update mid-session).")
            sys.exit(1)
        return True
    except Exception as e:
        print(f"!! preflight failed: {e}")
        sys.exit(1)


def fetch_url_for_job(job_id: str) -> str | None:
    """If we have a known URL, return it. Otherwise, the new session should
    call the MCP job_display tool to get the canonical URL."""
    for code, jid in JOBS.items():
        if jid == job_id and code in KNOWN_URLS:
            return KNOWN_URLS[code]
    return None


def download(url: str, dest: Path) -> Path:
    print(f"   downloading {url}")
    subprocess.run(
        ["curl", "-sL", "-o", str(dest), url],
        check=True
    )
    if dest.stat().st_size < 100_000:
        raise RuntimeError(f"download seems incomplete: {dest.stat().st_size} bytes")
    return dest


def composite(country: str, opener_path: Path):
    composite_script = HERE / "composite.py"
    subprocess.run(
        [sys.executable, str(composite_script), country, str(opener_path)],
        check=True
    )


def main():
    print(">>> preflight: checking cloudfront reachability")
    preflight()
    print("   ok\n")

    for code, job_id in JOBS.items():
        print(f">>> {code} ({job_id})")
        url = fetch_url_for_job(job_id)
        if not url:
            print(f"   ! no known URL — call job_display(\"{job_id}\") to get the URL")
            print(f"   ! then add to KNOWN_URLS and re-run")
            continue
        tmp = Path(f"/tmp/opener_{code}.mp4")
        try:
            download(url, tmp)
        except Exception as e:
            print(f"   ! download failed: {e}")
            continue
        try:
            composite(code, tmp)
        except Exception as e:
            print(f"   ! composite failed: {e}")
            continue
        tmp.unlink(missing_ok=True)
        print()


if __name__ == "__main__":
    main()
