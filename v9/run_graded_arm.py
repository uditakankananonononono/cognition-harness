"""v9-suite follow-up arm: run the v10 challenger (graded-fitness beam) on the
FROZEN v9 suite for direct comparison with v9 beam (68/80). Same budgets/judge.
Appends new receipts only; does not touch existing v9 receipts or frozen bytes.
"""
import json, subprocess, sys, time
from pathlib import Path
from isolation import R, score
from judge import verify
import proposer2

def main(pin):
    verify(pin)
    dev = json.loads((R/'frozen'/'dev.json').read_bytes())
    baseline = (R/'candidates'/'baseline.py').read_text()
    t0 = time.time()
    cand, hist = proposer2.beam(baseline, dev, score, use_distance=True)
    (R/'candidates'/'candidate-graded.py').write_text(cand)
    hist['wall_seconds'] = round(time.time() - t0, 3)
    (R/'receipts'/'dev-history-graded.json').write_text(json.dumps(hist, indent=1) + '\n')
    judged = subprocess.run([sys.executable, str(R/'judge.py'), pin, str(R/'candidates'/'baseline.py'),
                             str(R/'candidates'/'candidate-graded.py')], check=True, capture_output=True, text=True)
    (R/'receipts'/'graded-measurement.json').write_text(judged.stdout)
    m = json.loads(judged.stdout)
    c = m['candidates'][0]
    print(json.dumps({'baseline': m['baseline'].get('passed'),
                      'graded': {'frozen_passed': c['report'].get('passed'), 'per_task': c['report'].get('per_task'),
                                 'gate': c['measurement_gate'], 'executions': hist['executions'],
                                 'best_dev_passed': hist['best_dev_passed'], 'best_dev_distance': hist['best_dev_distance'],
                                 'wall_seconds': hist['wall_seconds']}}, indent=1))

if __name__ == '__main__':
    main(sys.argv[1])
