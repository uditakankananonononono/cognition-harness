"""Independent of proposer implementation; separate scoring process, fixed answers."""
import json, sys
from pathlib import Path
from isolation import R, sha, score

def verify(pin):
    manifest = (R/'frozen'/'MANIFEST.json').read_bytes()
    if sha(manifest) != pin: raise ValueError('manifest pin mismatch')
    for name, digest in json.loads(manifest).items():
        if sha((R/'frozen'/name).read_bytes()) != digest: raise ValueError('frozen bytes changed')

def promotion(baseline, candidate):
    if not baseline.get('valid') or not candidate.get('valid'): return False
    return candidate['passed'] > baseline['passed'] and all(candidate['per_task'][t] >= baseline['per_task'][t] for t in baseline['per_task'])

if __name__ == '__main__':
    verify(sys.argv[1])
    sources = [Path(p).read_bytes() for p in sys.argv[2:]]
    cases = json.loads((R/'frozen'/'eval.json').read_bytes())
    reports = [score(s, cases) for s in sources]
    verify(sys.argv[1])
    print(json.dumps({'manifest_pin': sys.argv[1], 'baseline': reports[0], 'candidates': [{'report': c, 'measurement_gate': promotion(reports[0], c), 'activation': 'pending_independent_review'} for c in reports[1:]]}, indent=2))
