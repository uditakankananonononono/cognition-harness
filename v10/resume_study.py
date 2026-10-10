"""Resume v10 study after interruption: run only missing arms, then judge."""
import json, subprocess, sys, time
from pathlib import Path
from isolation import R, score
from judge import verify
import proposer2

pin = (R/'receipts'/'frozen-pin.txt').read_text().strip()
verify(pin)
dev = json.loads((R/'frozen'/'dev.json').read_bytes())
baseline = (R/'candidates'/'baseline.py').read_text()
summary = {}
for arm in ['beam-binary', 'beam-graded']:
    hp = R/'receipts'/f'dev-history-{arm}.json'
    if hp.exists() and (R/'candidates'/f'candidate-{arm}.py').exists():
        h = json.loads(hp.read_bytes())
        summary[arm] = {'executions': h['executions'], 'best_dev_passed': h['best_dev_passed'],
                        'best_dev_distance': h.get('best_dev_distance'), 'resumed': True}
        continue
    t0 = time.time()
    cand, hist = proposer2.beam(baseline, dev, score, use_distance=(arm == 'beam-graded'))
    (R/'candidates'/f'candidate-{arm}.py').write_text(cand)
    (hp).write_text(json.dumps(hist, indent=1) + '\n')
    summary[arm] = {'wall_seconds': round(time.time() - t0, 3), 'changed_vs_baseline': cand != baseline,
                    'executions': hist['executions'], 'best_dev_passed': hist['best_dev_passed'],
                    'best_dev_distance': hist['best_dev_distance']}
arms = ['beam-binary', 'beam-graded']
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
