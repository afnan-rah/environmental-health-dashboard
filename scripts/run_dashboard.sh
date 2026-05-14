#!/usr/bin/env bash
# Run the Streamlit dashboard from the repo root (sets PYTHONPATH automatically).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ ! -d venv ]]; then
  echo "Missing venv/. Create it first: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi
# shellcheck source=/dev/null
source "$ROOT/venv/bin/activate"
export PYTHONPATH="$ROOT"
exec streamlit run "$ROOT/app.py" "$@"
