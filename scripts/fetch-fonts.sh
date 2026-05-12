#!/usr/bin/env bash
# fetch-fonts.sh — refresh the self-hosted JetBrains Mono Variable WOFF2.
#
# Idempotent. Run from anywhere; resolves output paths from this script's location.
#
# Usage:
#     bash scripts/fetch-fonts.sh
# Writes:
#     assets/fonts/jetbrains-mono-variable.woff2

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$HERE/../assets/fonts"
OUT_FILE="$OUT_DIR/jetbrains-mono-variable.woff2"

mkdir -p "$OUT_DIR"

PRIMARY="https://cdn.jsdelivr.net/fontsource/fonts/jetbrains-mono:vf@latest/latin-wght-normal.woff2"
FALLBACK="https://cdn.jsdelivr.net/npm/@fontsource-variable/jetbrains-mono@latest/files/jetbrains-mono-latin-wght-normal.woff2"

echo "fetching JetBrains Mono Variable (Latin subset) ..."
if ! curl -sSL --fail "$PRIMARY" -o "$OUT_FILE"; then
  echo "primary URL failed, trying fallback ..."
  curl -sSL --fail "$FALLBACK" -o "$OUT_FILE"
fi

SIZE=$(wc -c < "$OUT_FILE")
echo "wrote $OUT_FILE ($SIZE bytes)"

# Sanity check: WOFF2 files start with 'wOF2' (0x77 0x4F 0x46 0x32).
head -c 4 "$OUT_FILE" | grep -q '^wOF2' \
  || { echo "ERROR: $OUT_FILE is not a WOFF2 (magic mismatch)"; exit 1; }

echo "ok"
