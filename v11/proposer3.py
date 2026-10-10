"""v11 challenger: beam with BEHAVIORAL-DEDUP retention. Motivation (v9/v10
receipts): the binding constraint is plateau retention - width-8 slots are
wasted on children with identical dev behavior (commuting arg swaps, dead
renames). v11 groups scored children by their exact dev behavior vector and
keeps at most one representative per behavior, so all 8 slots are distinct
behaviors. Identical search space, budgets; one _better() ordering everywhere
(passed desc, distance asc, sha asc). Arms: dedup-binary, dedup-graded.

REPAIRED 2026-10-10: (a) baseline fitness was initialized with distance 0
instead of fitness(base_rep); (b) best-candidate used fit > best_fit, selecting
LARGER distance on equal pass; (c) behavior-representative tie-break compared
reversed sha descending instead of sha ascending. Suite-independent libraries
(mutations, fitness) are loaded by explicit path, not sys.path mutation.
"""
import hashlib, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_REPO = Path(__file__).resolve().parent.parent
mutations = _load('v9_mutations_lib', _REPO / 'v9' / 'mutations.py')
fitness_mod = _load('v10_fitness_lib', _REPO / 'v10' / 'fitness.py')
expand = mutations.expand
fitness = fitness_mod.fitness

sha = lambda b: hashlib.sha256(b).hexdigest()

def _better(fit, h, cur_fit, cur_h):
    """Single ordering: passed desc, distance asc, sha asc."""
    if fit[0] != cur_fit[0]:
        return fit[0] > cur_fit[0]
    if fit[1] != cur_fit[1]:
        return fit[1] < cur_fit[1]
    return h < cur_h

def _behavior_key(rep):
    if not rep.get('valid'):
        return ('invalid', rep.get('reason'))
    return ('valid', tuple((c['passed'], json.dumps(c.get('actual'), sort_keys=True) if 'actual' in c else None, c.get('error')) for c in rep['cases']))

def beam(source, dev, score, use_distance, width=8, depth=6, exec_cap=4000, jobs=8):
    history = []
    execs = 0
    base_rep = score(source.encode(), dev)
    execs += 1
    base_fit = fitness(base_rep) if use_distance else (base_rep.get('passed', -1), 0)
    total = base_rep.get('total', len(dev))
    base_sha = sha(source.encode())
    scored = {base_sha}
    frontier = [(base_fit, base_sha, source)]
    best_fit, best_sha, best_source = base_fit, base_sha, source
    for d in range(depth):
        if best_fit[0] == total or execs >= exec_cap or not frontier:
            break
        gen = []
        for pfit, psha, psrc in frontier:
            for desc, child in expand(psrc):
                h = sha(child.encode())
                if h not in scored:
                    scored.add(h)
                    gen.append((psha, desc, child, h))
        room = exec_cap - execs
        if room <= 0:
            break
        gen = gen[:room]
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            reports = list(ex.map(lambda g: score(g[2].encode(), dev), gen))
        execs += len(gen)
        by_behavior = {}
        for (psha, desc, child, h), rep in zip(gen, reports):
            fit = fitness(rep) if use_distance else (rep.get('passed', -1), 0)
            bkey = _behavior_key(rep)
            history.append({'depth': d, 'parent': psha[:12], 'desc': desc, 'sha': h[:12],
                            'valid': rep.get('valid', False), 'passed': rep.get('passed', -1),
                            'distance': fit[1],
                            'behavior': hashlib.sha256(repr(bkey).encode()).hexdigest()[:12]})
            cur = by_behavior.get(bkey)
            if cur is None or _better(fit, h, cur[0], cur[1]):
                by_behavior[bkey] = (fit, h, child)
            if _better(fit, h, best_fit, best_sha):
                best_fit, best_sha, best_source = fit, h, child
        children = sorted(by_behavior.values(), key=lambda t: (-t[0][0], t[0][1], t[1]))
        frontier = children[:width]
    distinct = len({t.get('behavior') for t in history})
    return best_source, {'width': width, 'depth_cap': depth, 'execution_cap': exec_cap,
                         'executions': execs, 'distinct_behaviors': distinct,
                         'best_dev_passed': best_fit[0], 'best_dev_distance': best_fit[1],
                         'dev_total': total, 'trials': history}
