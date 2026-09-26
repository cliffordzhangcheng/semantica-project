#!/usr/bin/env python3
"""Export the deterministic ONE-N524 v0.4 candidate contract bundle."""
from pathlib import Path

from semantica_workbench.export.one_n524_contract import export_bundle


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    hashes = export_bundle(ROOT, ROOT / "contracts/one-n524/v0.4.1")
    for name, value in hashes.items():
        print(f"{value}  {name}")
