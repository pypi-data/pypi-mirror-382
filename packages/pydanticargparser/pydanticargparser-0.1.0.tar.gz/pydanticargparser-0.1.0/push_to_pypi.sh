#!/usr/bin/env bash
set -euo pipefail

# --- config & helpers ------------------------------------------------------

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # Load .env safely (no word splitting)
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

usage() {
  cat <<'USAGE'
Usage: ./push_to_pypi.sh [--test] [--skip-build]

Builds the package and publishes it with uv.
Credentials are read from .env (PYPI_TOKEN="pypi-...").

Options:
  --test         Publish to TestPyPI (https://test.pypi.org/)
  --skip-build   Do not rebuild; upload existing ./dist artifacts
  -h, --help     Show this help
USAGE
}

PUBLISH_TO_TESTPYPI="${TESTPYPI_DEFAULT:-0}"
DO_BUILD=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --test)       PUBLISH_TO_TESTPYPI=1; shift ;;
    --skip-build) DO_BUILD=0; shift ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

# --- preflight checks ------------------------------------------------------

command -v uv >/dev/null 2>&1 || { echo "Error: uv is not installed. Install it (pip install uv) and retry."; exit 1; }

[[ -f "pyproject.toml" ]] || { echo "Error: pyproject.toml not found in repo root."; exit 1; }

# Require token for publishing (PyPI no longer accepts username/password)
: "${PYPI_TOKEN:?Error: PYPI_TOKEN not set. Put it in .env as PYPI_TOKEN=\"pypi-...\"}"

# Map to uv’s expected env var (see: docs.astral.sh/uv/guides/package/)
export UV_PUBLISH_TOKEN="${PYPI_TOKEN}"

# --- build -----------------------------------------------------------------

if [[ "$DO_BUILD" -eq 1 ]]; then
  echo "Building distributions with uv..."
  # Optional: add --no-sources for stricter build dependency resolution
  uv build
fi

# --- choose destination & publish -----------------------------------------

if [[ "$PUBLISH_TO_TESTPYPI" -eq 1 ]]; then
  echo "Publishing to TestPyPI…"
  # You can also define a named index in pyproject; here we use the built-in flag
  uv publish --repository testpypi
else
  echo "Publishing to PyPI…"
  uv publish
fi

echo "Done."
