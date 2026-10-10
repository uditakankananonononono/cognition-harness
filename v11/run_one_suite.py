"""v11 per-suite study worker. REPAIRED 2026-10-10: each suite runs in its OWN
process (this script is invoked per suite) and its judge/isolation are loaded
with sys.modules hygiene, so suite A's judge can never resolve suite B's
isolation.R (the defect the reviewer probed). Usage: run_one_suite.py <v9|v10>
"""
import json, subprocess, sys, time
from pathlib import Path
import importlib.util

ARMS = ['dedup-binary', 'dedup-graded']
REPO = Path(__file__).resolve().parent.parent

def load_suite(tag):
    suite_dir = (REPO / tag).resolve()
    # Hygiene: drop any previously loaded same-named modules, then put THIS
    # suite's directory first so `from isolation import ...` inside its judge
    # resolves to its own isolation.py (correct R) and nothing else's.
    for name in ('isolation', 'judge', 'worker'):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(suite_dir))
    try:
        isolation = importlib.import_module('isolation')
        judge = importlib.import_module('judge')
    finally:
        sys.path.remove(str(suite_dir))
    assert isolation.R == suite_dir, (isolation.R, suite_dir)
    proposer3_spec = importlib.util.spec_from_file_location('proposer3', REPO / 'v11' / 'proposer3.py')
    proposer3 = importlib.util.module_from_spec(proposer3_spec)
    proposer3_spec.loader.exec_module(proposer3)
    return suite_dir, isolation, judge, proposer3

def main(tag):
    suite_dir, isolation, judge, proposer3 = load_suite(tag)
    R = isolation.R
    pin = (R/'receipts'/'frozen-pin.txt').read_text().strip()
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
                            check=True, capture_output=True, text=True, cwd=str(R))
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
    main(sys.argv[1])
