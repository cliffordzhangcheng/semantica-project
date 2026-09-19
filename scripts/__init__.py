"""Legacy compatibility scripts - call semantica_workbench CLI"""
import sys
from pathlib import Path

def _main(script_name: str):
    """Route legacy script calls to semantica_workbench CLI"""
    from semantica_workbench.cli import main
    return main()

if __name__ == "__main__":
    sys.exit(_main(Path(__file__).stem))
