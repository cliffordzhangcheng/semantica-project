#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "Semantica Golden Relations v0.4 Pipeline"
echo "=========================================="

# Record start
MAIN_SHA=$(git rev-parse main)
echo "Main branch SHA: $MAIN_SHA"

# Clean rebuild
echo ""
echo "[Step 1] Clean rebuild..."
rm -rf outputs/
python3 -m semantica_workbench.cli run 2>&1 | tail -5

# Build golden relations
echo ""
echo "[Step 2] Building Golden Relations..."
python3 scripts/build_golden_relations.py

# Determinism validation
echo ""
echo "[Step 3] Running determinism validation..."
python3 scripts/determinism_validator.py

# Run gates
echo ""
echo "[Step 4] Running gates..."
python3 scripts/run_gates.py --project-root .

# Generate report
echo ""
echo "[Step 5] Generating report..."
python3 scripts/generate_golden_report.py

# Verify main unchanged
echo ""
echo "[Step 6] Verifying main unchanged..."
CURRENT_SHA=$(git rev-parse main)
if [ "$MAIN_SHA" != "$CURRENT_SHA" ]; then
    echo "❌ FOUNDER BOUNDARY VIOLATED: main changed during execution"
    exit 1
fi
echo "✅ Main unchanged: $MAIN_SHA"

echo ""
echo "=========================================="
echo "Pipeline Complete"
echo "=========================================="
