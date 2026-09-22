"""Run regressions and fresh rebuilds, then bind their evidence to this commit."""
import argparse
from pathlib import Path
import subprocess
import sys

from semantica_workbench.pipeline.golden import digest, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip():
        raise ValueError('Verification requires a clean committed checkout')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    tests = output / 'tests.xml'
    subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-q', f'--junitxml={tests}'], cwd=root, check=True)
    subprocess.run([sys.executable, '-m', 'semantica_workbench.cli', 'closure',
                    '--output', str(output / 'closure')], cwd=root, check=True)
    write_json(output / 'verification.json', {'head_sha': head, 'tests_hash': digest(tests.read_text()),
                                            'closure_hash': digest((output / 'closure/closure.json').read_text())})


if __name__ == '__main__':
    main()
