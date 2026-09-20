#!/bin/bash
set -euo pipefail
# Run all pipeline stages via unified CLI
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
exec python -m semantica_workbench.cli run --project-root "$PROJECT_ROOT" "$@"
