"""v9 study runner: verify freeze, run arms, judge each candidate ONCE on the
frozen eval, retain all receipts. No arm sees eval inputs or expected outputs.
"""
import json, subprocess, sys, time
from pathlib import Path
from isolation import R
from judge import verify
import proposer

def main(pin):
    verify(pin)
    dev = json.loads((R/'frozen'/'dev.json').read_bytes())
    baseline = (R/'candidates'/'baseline.py').read_text()
    (R/'receipts').mkdir(exist_ok=True)
    arms = ['menu', 'beam', 'beam-macro']
    summary = {}
    for arm in arms:
        t0 = time.time()
        if arm == 'menu':
            cand, hist = proposer.menu(baseline, dev)
        else:
            cand, hist = proposer.beam(baseline, dev, use_macros=(arm == 'beam-macro'))
        (R/'candidates'/f'candidate-{arm}.py').write_text(cand)
        (R/'receipts'/f'dev-history-{arm}.json').write_text(json.dumps(hist, indent=1) + '\n')
        summary[arm] = {'wall_seconds': round(time.time() - t0, 3), 'changed_vs_baseline': cand != baseline,
                        'executions': hist['executions'], 'best_dev_passed': hist.get('best_dev_passed')}
    judged = subprocess.run([sys.executable, str(R/'judge.py'), pin, str(R/'candidates'/'baseline.py')]
                            + [str(R/'candidates'/f'candidate-{a}.py') for a in arms],
                            check=True, capture_output=True, text=True)
    (R/'receipts'/'study-measurement.json').write_text(judged.stdout)
    measurement = json.loads(judged.stdout)
    out = {'manifest_pin': pin, 'baseline_passed': measurement['baseline'].get('passed'),
           'baseline_per_task': measurement['baseline'].get('per_task'), 'arms': {}}
    for arm, cand in zip(arms, measurement['candidates']):
        out['arms'][arm] = {**summary[arm], 'frozen_passed': cand['report'].get('passed'),
                            'frozen_per_task': cand['report'].get('per_task'),
                            'measurement_gate': cand['measurement_gate'], 'activation': cand['activation']}
    (R/'receipts'/'study.json').write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    main(sys.argv[1])
