#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m semantica_workbench.cli run