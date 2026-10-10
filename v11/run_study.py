"""v11 full study: dedup-binary and dedup-graded arms on BOTH frozen suites.
Judge each arm ONCE per suite. Receipts per suite in the suite's own dir.
Usage: python3 run_study.py <v9|v10|both>
"""
import json, subprocess, sys, time
from pathlib import Path
import importlib.util

V9 = Path(__file__).resolve().parent.parent / 'v9'
V10D = Path(__file__).resolve().parent.parent / 'v10'
ARMS = ['dedup-binary', 'dedup-graded']

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def run_suite(tag, suite_dir):
    isolation = load(f'isolation_{tag}', suite_dir / 'isolation.py')
    proposer3 = load('proposer3', Path(__file__).resolve().parent / 'proposer3.py')
    R = isolation.R
    pin = (R/'receipts'/'frozen-pin.txt').read_text().strip()
    # manifest verify via that suite's judge
    judge = load(f'judge_{tag}', suite_dir / 'judge.py')
    judge.verify(pin)
    dev = json.loads((R/'frozen'/'dev.json').read_bytes())
    baseline = (R/'candidates'/'baseline.py').read_text()
    summary = {}
    for arm in ARMS:
        t0 = time.time()
        cand, hist = proposer3.beam(baseline, dev, isolation.score, use_distance=(arm == 'dedup-graded'))
        (R/'candidates'/f'candidate-{arm}.py').write_text(cand)
        hist['wall_seconds'] = round(time.time() - t0, 3)
        (R/'receipts'/f'dev-history-{arm}.json').write_text(json.dumps(hist, indent=1) + '\n')
        summary[arm] = {'wall_seconds': hist['wall_seconds'], 'changed_vs_baseline': cand != baseline,
                        'executions': hist['executions'], 'distinct_behaviors': hist['distinct_behaviors'],
                        'best_dev_passed': hist['best_dev_passed'], 'best_dev_distance': hist['best_dev_distance']}
    judged = subprocess.run([sys.executable, str(R/'judge.py'), pin, str(R/'candidates'/'baseline.py')]
                            + [str(R/'candidates'/f'candidate-{a}.py') for a in ARMS],
                            check=True, capture_output=True, text=True)
    (R/'receipts'/f'v11-measurement-{tag}.json').write_text(judged.stdout)
    m = json.loads(judged.stdout)
    out = {'suite': tag, 'manifest_pin': pin, 'baseline_passed': m['baseline'].get('passed'),
           'baseline_per_task': m['baseline'].get('per_task'), 'arms': {}}
    for arm, cand in zip(ARMS, m['candidates']):
        out['arms'][arm] = {**summary[arm], 'frozen_passed': cand['report'].get('passed'),
                            'frozen_per_task': cand['report'].get('per_task'),
                            'measurement_gate': cand['measurement_gate'], 'activation': cand['activation']}
    (R/'receipts'/f'v11-study-{tag}.json').write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    if which in ('v9', 'both'):
        run_suite('v9', V9)
    if which in ('v10', 'both'):
        run_suite('v10', V10D)
