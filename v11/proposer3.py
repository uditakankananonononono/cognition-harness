"""v11 challenger: beam with BEHAVIORAL-DEDUP retention. Motivation (v9/v10
receipts): the binding constraint is plateau retention - width-8 slots are
wasted on children with identical dev behavior (commuting arg swaps, dead
renames). v11 groups scored children by their exact dev behavior vector and
keeps at most one representative per behavior, so all 8 slots are distinct
behaviors. Identical search space, budgets, ranking within a behavior
(passed desc, sha asc). Arms: dedup-binary (rank by passed) and dedup-graded
(passed, then v10 value-distance).
"""
import hashlib, json, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'v9'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'v10'))
from mutations import expand
from fitness import fitness

def _behavior_key(rep):
    if not rep.get('valid'):
        return ('invalid', rep.get('reason'))
    return ('valid', tuple((c['passed'], json.dumps(c.get('actual'), sort_keys=True) if 'actual' in c else None, c.get('error')) for c in rep['cases']))

def beam(source, dev, score, use_distance, width=8, depth=6, exec_cap=4000, jobs=8):
    sha = lambda b: hashlib.sha256(b).hexdigest()
    history = []
    execs = 0
    base_rep = score(source.encode(), dev)
    execs += 1
    total = base_rep.get('total', len(dev))
    scored = {sha(source.encode())}
    frontier = [((base_rep.get('passed', -1), 0), sha(source.encode()), source)]
    best_fit, best_source = frontier[0][0], source
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
                            'distance': fit[1], 'behavior': hashlib.sha256(repr(bkey).encode()).hexdigest()[:12]})
            key = _behavior_key(rep)
            cur = by_behavior.get(key)
            if cur is None or (fit[0], -fit[1], tuple(reversed(h))) > (cur[0][0], -cur[0][1], tuple(reversed(cur[1]))):
                by_behavior[key] = (fit, h, child)
            if fit > best_fit:
                best_fit, best_source = fit, child
        children = sorted(by_behavior.values(), key=lambda t: (-t[0][0], t[0][1], t[1]))
        frontier = children[:width]
    distinct = len({t.get('behavior') for t in history})
    return best_source, {'width': width, 'depth_cap': depth, 'execution_cap': exec_cap,
                         'executions': execs, 'distinct_behaviors': distinct,
                         'best_dev_passed': best_fit[0], 'best_dev_distance': best_fit[1],
                         'dev_total': total, 'trials': history}
