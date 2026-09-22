"""Create final evidence only after local gates, regression tests and branch CI agree."""
import argparse
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from semantica_workbench.evaluation.closure import validate, compare
from semantica_workbench.pipeline.golden import read_json, write_json, digest

BASE = 'eb8af3b949142b83303b9f87f8d06d7d7bd99489'
BRANCH = 'codex/semantica-runtime-closure-v1'


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def test_counts(path):
    suites = ET.parse(path).getroot()
    cases = list(suites.iter('testcase'))
    failures = sum(case.find('failure') is not None or case.find('error') is not None for case in cases)
    skipped = sum(case.find('skipped') is not None for case in cases)
    return {'passed': len(cases) - failures - skipped, 'failed': failures, 'skipped': skipped}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--closure', type=Path, required=True)
    parser.add_argument('--tests', type=Path, required=True)
    parser.add_argument('--ci', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    branch = git(root, 'branch', '--show-current')
    head = git(root, 'rev-parse', 'HEAD')
    main_finish = git(root, 'ls-remote', 'origin', 'refs/heads/main').split()[0]
    if branch != BRANCH or main_finish != BASE or git(root, 'status', '--porcelain'):
        raise ValueError('Branch/main/clean-checkout boundary failed')
    ci = read_json(args.ci)
    if ci['headSha'] != head or ci['headBranch'] != branch or ci['conclusion'] != 'success' or ci['status'] != 'completed':
        raise ValueError('CI is not successful for current branch HEAD')
    binding = read_json(args.tests.parent / 'verification.json')
    if (binding['head_sha'] != head or binding['tests_hash'] != digest(args.tests.read_text())
            or binding['closure_hash'] != digest((args.closure / 'closure.json').read_text())):
        raise ValueError('Verification evidence is not bound to current HEAD')
    counts = test_counts(args.tests)
    if counts['passed'] < 65 or counts['failed'] or counts['skipped']:
        raise ValueError('Regression test threshold not met')
    gates = validate(root, args.closure / 'run1')
    gates['GDET'] = compare(root, args.closure / 'run1', args.closure / 'run2')
    previous = read_json(args.closure / 'closure.json')
    if gates != previous['gates'] or any(g['status'] != 'PASS' for g in gates.values()):
        raise ValueError('Machine gates failed or recorded results drifted')
    receipt = {
        'branch': branch, 'base_sha': git(root, 'merge-base', 'HEAD', BASE), 'head_sha': head,
        'main_sha_start': BASE, 'main_sha_finish': main_finish,
        'openminis_disposition': 'docs/runtime-closure-audit.md',
        'runtime': read_json(args.closure / 'run1/report.json'),
        'gates': gates, 'tests': counts, 'ci': ci,
        'main_changed': main_finish != BASE,
        'production_changes': 'No production mutation is part of this pipeline',
        'limitations': ['Curated corpus assertions only; no independent business-data authentication',
                        'Exact reviewed catalog, not general semantic entailment',
                        'Three admitted candidates; PUC and generic container candidate rejected',
                        'G6 BLOCKED; independent review and Founder G7 merge decision pending'],
        'final_status': 'SEMANTICA_ENGINEERING_BASELINE_PASS_CANDIDATE — PENDING_FOUNDER_G7',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
