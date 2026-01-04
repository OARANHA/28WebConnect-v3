#!/usr/bin/env bash
set -euo pipefail

POSTMAN_JSON="Evolution-API-v2.3.-.postman_collection.json"
OUT_DIR="static/docs"
OUT_FILE="$OUT_DIR/evolution-openapi.yaml"

# Find project root (this script is expected to run from repo root, but we adapt)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

if [ ! -f "$POSTMAN_JSON" ]; then
  echo "[docs] Postman collection not found at: $POSTMAN_JSON" >&2
  echo "[docs] Please place it at repo root or adjust the script path." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

# Ensure postman-to-openapi is available
if ! command -v npx >/dev/null 2>&1; then
  echo "[docs] npx not found. Please install Node.js >= 18." >&2
  exit 1
fi

echo "[docs] Converting Postman collection to OpenAPI..."
# Use npx to run without global install; -p to resolve path params
npx postman-to-openapi "$POSTMAN_JSON" "$OUT_FILE" -p

if [ -f "$OUT_FILE" ]; then
  echo "[docs] OpenAPI generated at: $OUT_FILE"
else
  echo "[docs] Failed to generate OpenAPI file." >&2
  exit 1
fi
