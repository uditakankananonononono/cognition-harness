"""v9 frozen suite construction. Run once before any scoring; prints manifest pin.
Five task families x 16 hand-authored eval cases (80 total), 2 dev cases each (10 total).
Baseline bugs are deliberately NOT text-matched by the incumbent M1 repair menu.
Expected outputs are literal hand-authored values, verified against independent
reference implementations by tests.py, never computed from candidate code.
"""
import hashlib, json
from pathlib import Path
R = Path(__file__).resolve().parent

BASELINE = '''def clamp_range(values):
    x, lo, hi = values
    return min(max(x, lo), lo)


def second_largest(nums):
    return sorted(set(nums))[0]


def count_even(nums):
    return sum(1 for n in nums if n % 2 == 1)


def running_max(nums):
    out = []
    m = nums[0]
    for n in nums:
        m = min(m, n)
        out.append(m)
    return out


def first_above(pair):
    values, limit = pair
    for v in values:
        if v >= limit:
            return limit
    return None
'''

cases = []
def add(task, pairs):
    for i, (x, y) in enumerate(pairs):
        cases.append(dict(id=f'{task}-{i:02d}', task=task, input=x, expected=y))

add('clamp_range', [
    ([7,0,10],7), ([-4,0,10],0), ([15,0,10],10), ([3,2,8],3),
    ([1,2,8],2), ([12,2,8],8), ([0,-5,5],0), ([-9,-5,5],-5),
    ([9,-5,5],5), ([-3,-7,-1],-3), ([-10,-7,-1],-7), ([0,-7,-1],-1),
    ([4,4,4],4), ([5,4,4],4), ([3,4,4],4), ([-100,-1,0],-1),
])
add('second_largest', [
    ([1,2],1), ([2,1],1), ([5,5,9],5), ([0,-1],-1),
    ([-3,-1,-2],-2), ([10,20,30],20), ([3,3,3,1],1), ([8,2,8,2],2),
    ([100,50,75],75), ([-5,0,5],0), ([4,4,4,4,6],4), ([9,1,9,1,9],1),
    ([7,3,11,3],7), ([0,0,2,2,1],1), ([-10,-20,-30],-20), ([6,6,5],5),
])
add('count_even', [
    ([],0), ([2],1), ([1],0), ([2,4],2),
    ([1,3],0), ([1,2],1), ([0],1), ([0,1,2,3,4,5],3),
    ([7,7,7],0), ([10,21,30,41],2), ([-2,-4],2), ([-1,-3],0),
    ([100,101],1), ([5,10,15,20],2), ([8],1), ([3,6,9,12],2),
])
add('running_max', [
    ([1],[1]), ([1,2],[1,2]), ([2,1],[2,2]), ([1,2,3],[1,2,3]),
    ([3,2,1],[3,3,3]), ([1,3,2,4],[1,3,3,4]), ([5,1,5,1],[5,5,5,5]), ([0,-1,2,-2],[0,0,2,2]),
    ([-3,-1,-2],[-3,-1,-1]), ([2,2,2],[2,2,2]), ([4,0,9,9,1],[4,4,9,9,9]), ([10],[10]),
    ([-5,-6,-4],[-5,-5,-4]), ([1,1,2,0,3],[1,1,2,2,3]), ([7,8,6],[7,8,8]), ([0,0,-1],[0,0,0]),
])
add('first_above', [
    ([[1,2,3],1],2), ([[1,1,1],1],None), ([[5],3],5), ([[5],5],None),
    ([[],0],None), ([[0,-1,-2],-2],0), ([[3,3,4],3],4), ([[10,9,8],9],10),
    ([[2,2],2],None), ([[-5,0,5],0],5), ([[7,7,7],6],7), ([[1,4,4,2],4],None),
    ([[9,1,1],8],9), ([[0,0,1],0],1), ([[6,5],5],6), ([[2,3,4],4],None),
])

dev = [
    {'id':'dev-clamp','task':'clamp_range','input':[6,1,9],'expected':6},
    {'id':'dev-clamp2','task':'clamp_range','input':[20,1,9],'expected':9},
    {'id':'dev-second','task':'second_largest','input':[5,1,3],'expected':3},
    {'id':'dev-second2','task':'second_largest','input':[10,10,4,4,7],'expected':7},
    {'id':'dev-count','task':'count_even','input':[2,4,6],'expected':3},
    {'id':'dev-count2','task':'count_even','input':[1,3,5,2],'expected':1},
    {'id':'dev-running','task':'running_max','input':[1,3,2],'expected':[1,3,3]},
    {'id':'dev-running2','task':'running_max','input':[2,1,4],'expected':[2,2,4]},
    {'id':'dev-first','task':'first_above','input':[[1,5,3],2],'expected':5},
    {'id':'dev-first2','task':'first_above','input':[[4,4],4],'expected':None},
]

(R/'candidates').mkdir(exist_ok=True)
(R/'candidates'/'baseline.py').write_text(BASELINE)
baseline_sha = hashlib.sha256(BASELINE.encode()).hexdigest()

protocol = {
    'version': 'v9.0',
    'tasks': ['clamp_range','second_largest','count_even','running_max','first_above'],
    'domain': ('clamp_range: [x,lo,hi] with lo<=hi, clamp x into [lo,hi]; '
               'second_largest: int list with >=2 distinct values, second largest distinct; '
               'count_even: int list, count of even values; '
               'running_max: nonempty int list, running maximum list; '
               'first_above: [values,limit], first v in values with v>limit else null'),
    'score': 'exact JSON equality, 80 equal-weight cases, 16 per task',
    'promotion': 'candidate total strictly increases AND each task pass count does not decrease',
    'arms': {
        'menu': 'incumbent M1 proposer: 3 named textual repair operators, dev-score hill climb, 3 rounds',
        'beam': 'inventive proposer: beam search over AST primitive transforms, dev-score ranking only',
        'beam-macro': 'beam plus cross-site macro-operator reuse extracted from improving mutations',
    },
    'budget': {'beam_width': 8, 'beam_depth': 6, 'execution_cap': 4000, 'jobs': 8},
    'resources': {'wall_seconds': 3, 'cpu_seconds': 1, 'address_space_bytes': 134217728, 'output_bytes': 65536},
    'baseline_sha256': baseline_sha,
    'seed': 0,
    'limitations': ['synthetic hand-authored tasks', 'no statistical generalization claim',
                    'mutation grammar is builder-chosen; no novel-operator invention claim',
                    'dev-set-driven search can overfit dev cases; frozen eval is the only held-out evidence',
                    'holdout not cryptographically hidden from author', 'no publication or product activation'],
}
for name, data in [('eval.json', cases), ('protocol.json', protocol), ('dev.json', dev)]:
    (R/'frozen'/name).write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'frozen').glob('*.json'))}
(R/'frozen'/'MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
print(hashlib.sha256((R/'frozen'/'MANIFEST.json').read_bytes()).hexdigest())
