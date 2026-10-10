"""v10 challenger proposer: v9 beam with optional graded-fitness ranking.
Identical search space, budgets and determinism; only the ranking key changes:
(passed desc) then (dev value-distance asc) then (source sha asc).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'v9'))
from concurrent.futures import ThreadPoolExecutor
from mutations import expand
import importlib, json

def beam(source, dev, score, use_distance, width=8, depth=6, exec_cap=4000, jobs=8):
    from fitness import fitness
    history = []
    execs = 0
    base_rep = score(source.encode(), dev)
    execs += 1
    base_fit = fitness(base_rep) if use_distance else (base_rep.get('passed', -1), 0)
    total = base_rep.get('total', len(dev))
    import hashlib
    sha = lambda b: hashlib.sha256(b).hexdigest()
    scored = {sha(source.encode())}
    frontier = [(base_fit, sha(source.encode()), source)]
    best_fit, best_source = base_fit, source
    for d in range(depth):
        if best_fit[0] == total or execs >= exec_cap or not frontier:
            break
        gen = []
        for pfit, psha, psrc in frontier:
            for desc, child in expand(psrc):
                h = sha(child.encode())
                if h not in scored:
                    scored.add(h)
                    gen.append((pfit, psha, desc, child, h))
        room = exec_cap - execs
        if room <= 0:
            break
        gen = gen[:room]
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            reports = list(ex.map(lambda g: score(g[3].encode(), dev), gen))
        execs += len(gen)
        children = []
        for (pfit, psha, desc, child, h), rep in zip(gen, reports):
            fit = fitness(rep) if use_distance else (rep.get('passed', -1), 0)
            history.append({'depth': d, 'parent': psha[:12], 'desc': desc, 'sha': h[:12],
                            'valid': rep.get('valid', False), 'passed': rep.get('passed', -1),
                            'distance': fit[1]})
            children.append((fit, h, child))
            if fit > best_fit:
                best_fit, best_source = fit, child
        children.sort(key=lambda t: (-t[0][0], t[0][1], t[1]))
        frontier = children[:width]
    return best_source, {'width': width, 'depth_cap': depth, 'execution_cap': exec_cap,
                         'executions': execs, 'best_dev_passed': best_fit[0],
                         'best_dev_distance': best_fit[1], 'dev_total': total, 'trials': history}
