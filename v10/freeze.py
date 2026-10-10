"""v10 frozen suite: PLATEAU suite. Every bug requires >=2 coordinated primitive
edits; no single edit improves dev (asserted by tests.py). Built to measure
fitness shaping (v10 graded beam) against binary ranking (v9 beam incumbent).
Freeze before any scoring; prints manifest pin.
"""
import hashlib, json
from pathlib import Path
R = Path(__file__).resolve().parent

BASELINE = '''def scale_offset(x):
    return x * 3 - 1


def in_open_interval(values):
    x, lo, hi = values
    return lo <= x or x <= hi


def sign3(x):
    if x >= 0:
        return 1
    if x <= 0:
        return -1
    return 0


def midpoint(pair):
    lo, hi = pair
    return (lo - hi) // 3


def evens_list(nums):
    return [n for n in nums if n % 3 == 1]
'''

cases = []
def add(task, pairs):
    for i, (x, y) in enumerate(pairs):
        cases.append(dict(id=f'{task}-{i:02d}', task=task, input=x, expected=y))

add('scale_offset', [
    (0,1), (1,3), (2,5), (3,7), (-1,-1), (-2,-3), (5,11), (-5,-9),
    (10,21), (-10,-19), (7,15), (-3,-5), (4,9), (-4,-7), (100,201), (-100,-199),
])
add('in_open_interval', [
    ([5,0,10],True), ([0,0,10],False), ([10,0,10],False), ([-1,0,10],False),
    ([11,0,10],False), ([3,2,8],True), ([2,2,8],False), ([8,2,8],False),
    ([0,-5,5],True), ([-5,-5,5],False), ([5,-5,5],False), ([-6,-5,5],False),
    ([6,-5,5],False), ([1,1,2],False), ([-3,-7,-1],True), ([-1,-7,-1],False),
])
add('sign3', [
    (5,1), (-5,-1), (0,0), (1,1), (-1,-1), (100,1), (-100,-1), (2,1),
    (-2,-1), (9,1), (-9,-1), (7,1), (-7,-1), (42,1), (-42,-1), (13,1),
])
add('midpoint', [
    ([0,4],2), ([2,4],3), ([1,5],3), ([0,10],5),
    ([3,9],6), ([2,2],2), ([0,1],0), ([5,15],10),
    ([-4,4],0), ([-6,0],-3), ([10,20],15), ([-3,3],0),
    ([7,8],7), ([0,100],50), ([-10,10],0), ([4,6],5),
])
add('evens_list', [
    ([],[]), ([1],[]), ([2],[2]), ([1,2,3,4],[2,4]),
    ([3,5,7],[]), ([2,4,6],[2,4,6]), ([0],[0]), ([0,1,2],[0,2]),
    ([-2,-4],[-2,-4]), ([-1,-3],[]), ([10,21,30,41],[10,30]), ([5,10,15,20],[10,20]),
    ([8,9,10],[8,10]), ([3,6,9,12],[6,12]), ([100,101,102],[100,102]), ([-5,-6],[-6]),
])

dev = [
    {'id':'dev-scale','task':'scale_offset','input':6,'expected':13},
    {'id':'dev-scale2','task':'scale_offset','input':8,'expected':17},
    {'id':'dev-interval','task':'in_open_interval','input':[0,0,9],'expected':False},
    {'id':'dev-interval2','task':'in_open_interval','input':[9,0,9],'expected':False},
    {'id':'dev-sign','task':'sign3','input':0,'expected':0},
    {'id':'dev-sign2','task':'sign3','input':7,'expected':1},
    {'id':'dev-mid','task':'midpoint','input':[4,10],'expected':7},
    {'id':'dev-mid2','task':'midpoint','input':[1,9],'expected':5},
    {'id':'dev-evens','task':'evens_list','input':[6,3],'expected':[6]},
    {'id':'dev-evens2','task':'evens_list','input':[1,3,6],'expected':[6]},
]

(R/'candidates').mkdir(exist_ok=True)
(R/'candidates'/'baseline.py').write_text(BASELINE)
baseline_sha = hashlib.sha256(BASELINE.encode()).hexdigest()

protocol = {
    'version': 'v10.0',
    'tasks': ['scale_offset','in_open_interval','sign3','midpoint','evens_list'],
    'domain': ('scale_offset: int x -> 2x+1; in_open_interval: [x,lo,hi] lo<hi -> lo<x<hi; '
               'sign3: int -> 1/-1/0 by sign; midpoint: [lo,hi] -> floor((lo+hi)/2); '
               'evens_list: int list -> its even elements in order'),
    'plateau_property': ('every bug needs >=2 coordinated primitive edits; no single edit improves dev (tested). '
                         'in_open_interval needs 3 edits and emits boolean outputs: distance shaping gives no '
                         'signal there by construction - included as a no-signal control task'),
    'score': 'exact JSON equality, 80 equal-weight cases, 16 per task',
    'promotion': 'candidate total strictly increases AND each task pass count does not decrease',
    'arms': {
        'beam-binary': 'v9 incumbent: beam search, ranking by dev passed only',
        'beam-graded': 'v10 challenger: identical search/budgets, ranking ties broken by dev value-distance',
    },
    'budget': {'beam_width': 8, 'beam_depth': 6, 'execution_cap': 4000, 'jobs': 8},
    'resources': {'wall_seconds': 3, 'cpu_seconds': 1, 'address_space_bytes': 134217728, 'output_bytes': 65536},
    'baseline_sha256': baseline_sha,
    'seed': 0,
    'limitations': ['synthetic hand-authored tasks', 'distance heuristic is builder-chosen',
                    'sign3 bug is a single edge case (x=0) by construction; only 1/16 eval cases discriminate it',
                    'holdout not cryptographically hidden from author', 'no AGI or novelty claim',
                    'no publication or product activation'],
}
for name, data in [('eval.json', cases), ('protocol.json', protocol), ('dev.json', dev)]:
    (R/'frozen'/name).write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'frozen').glob('*.json')) if p.name != 'MANIFEST.json'}
(R/'frozen'/'MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
print(hashlib.sha256((R/'frozen'/'MANIFEST.json').read_bytes()).hexdigest())
