#!/usr/bin/env bash
# Download the 12 wc_turkey_dream scene MP4s from CloudFront into output/wc_turkey_raw/.
# Run this from any machine that can reach d8j0ntlcm91z4.cloudfront.net
# (i.e., NOT inside the Claude Code web environment that's blocking the host).
#
# Usage:
#   cd world-cup-loops
#   bash pieces/wc_turkey_dream/download_scenes.sh
#
# After it finishes, commit the output/wc_turkey_raw/ directory (or push it
# back to the branch), then re-run:
#   python pieces/wc_turkey_dream/build_long_form.py

set -euo pipefail
cd "$(dirname "$0")/../.."   # → world-cup-loops/
mkdir -p output/wc_turkey_raw

declare -A SCENES=(
  [s01_calm]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230153_3e70339d-e95f-464f-a232-0c3e4605435f.mp4"
  [s02_goal]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230156_7d7cb32a-af00-4fee-b2be-66fdd2c31873.mp4"
  [s03_galata]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230329_c44a0788-bcd2-4283-80e1-566597fa368f.mp4"
  [s04_dervish]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230334_b1d873de-7ab3-4f05-88c9-cab82e7a96fe.mp4"
  [s05_cappadocia]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230210_d608eb01-b4fb-4a14-85d6-beb44dd1d4d0.mp4"
  [s06_bosphorus]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230338_2ba13dab-1887-45de-859c-f42ce3779a15.mp4"
  [s07b_unity]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230515_aa2937f1-13d5-4761-93d1-6ffe557d3fac.mp4"
  [s08b_simit]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230220_8b82c2e4-000f-49b2-8de5-de4fbfec0a9c.mp4"
  [s07_cats]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230413_dc54dc8f-ce6d-438f-9486-a2543aac72ac.mp4"
  [s08_baklava]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230631_13c69c95-2827-4cf9-b8ce-51dbf5873c0e.mp4"
  [s09_taksim]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230636_09bc517d-05cf-4fa9-aaec-440bdcf2783b.mp4"
  [s10_wake]="https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230804_54bbe8a0-8167-4384-89dc-2b23f6dc66d5.mp4"
)

for sid in "${!SCENES[@]}"; do
  dst="output/wc_turkey_raw/${sid}.mp4"
  if [[ -s "$dst" ]]; then
    echo "✓ ${sid}.mp4 already present, skipping"
    continue
  fi
  echo "↓ ${sid}.mp4"
  curl -sSf -o "$dst" "${SCENES[$sid]}"
done

echo
echo "All 12 scenes downloaded to output/wc_turkey_raw/"
echo "Now run: python pieces/wc_turkey_dream/build_long_form.py"
