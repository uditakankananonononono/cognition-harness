"""v10 challenger proposer: v9 beam with optional graded-fitness ranking.
Identical search space, budgets and determinism; only the ranking key changes:
(passed desc) then (dev value-distance ASC) then (source sha asc).
REPAIRED 2026-10-10: best-candidate selection used fit > best_fit on
(passed, positive distance), selecting LARGER distance on equal pass -
opposite the frontier ranking. Now one _better() defines the order everywhere.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'v9'))  # mutations
sys.path.insert(0, str(Path(__file__).resolve().parent))  # fitness
from concurrent.futures import ThreadPoolExecutor
from mutations import expand
from fitness import fitness
import hashlib

sha = lambda b: hashlib.sha256(b).hexdigest()

def _better(fit, h, cur_fit, cur_h):
    """Single ordering: passed desc, distance asc, sha asc."""
    if fit[0] != cur_fit[0]:
        return fit[0] > cur_fit[0]
    if fit[1] != cur_fit[1]:
        return fit[1] < cur_fit[1]
    return h < cur_h

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
            if _better(fit, h, best_fit, best_sha):
                best_fit, best_sha, best_source = fit, h, child
        children.sort(key=lambda t: (-t[0][0], t[0][1], t[1]))
        frontier = children[:width]
    return best_source, {'width': width, 'depth_cap': depth, 'execution_cap': exec_cap,
                         'executions': execs, 'best_dev_passed': best_fit[0],
                         'best_dev_distance': best_fit[1], 'dev_total': total, 'trials': history}
