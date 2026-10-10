"""v9 proposers. menu = incumbent M1 behavior (control). beam = inventive search.
Dev-set scoring only; frozen eval is never touched here. All trials retained.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from isolation import R, score, sha
from mutations import expand, extract_macro

REPAIRS = [('canonical_whitespace', "text.lower().split(' ')", 'text.lower().split()'),
           ('unique_order', 'sorted(set(items))', 'list(dict.fromkeys(items))'),
           ('merge_touching', 'start < out[-1][1]', 'start <= out[-1][1]')]

def menu(source, dev):
    """Incumbent M1 proposer, verbatim logic: 3 rounds, named textual operators."""
    history = []
    current = score(source.encode(), dev)
    for round_no in range(3):
        trials = []
        for name, old, new in REPAIRS:
            if old in source:
                proposal = source.replace(old, new, 1)
                report = score(proposal.encode(), dev)
                trials.append((report.get('passed', -1), name, proposal, report))
        history.append({'round': round_no, 'dev_before': current.get('passed'),
                        'trials': [{'operator': t[1], 'report_passed': t[3].get('passed')} for t in trials]})
        if not trials:
            break
        best = max(trials, key=lambda t: (t[0], t[1]))
        if best[0] <= current['passed']:
            break
        source = best[2]
        current = best[3]
    return source, {'arm': 'menu', 'rounds': history, 'executions': sum(len(r['trials']) for r in history) + 1}

def beam(source, dev, use_macros, width=8, depth=6, exec_cap=4000, jobs=8):
    """Beam search over the AST mutation space. Ranking: dev passed desc, source
    sha asc (deterministic tie-break, no heuristic peeking at eval)."""
    history = []
    macros = []
    execs = 0
    base_rep = score(source.encode(), dev)
    execs += 1
    total = base_rep.get('total', len(dev))
    base_sha = sha(source.encode())
    scored = {base_sha}
    frontier = [(base_rep.get('passed', -1), base_sha, source)]
    best_passed, best_source = base_rep.get('passed', -1), source
    for d in range(depth):
        if best_passed == total or execs >= exec_cap or not frontier:
            break
        gen = []
        for ppassed, psha, psrc in frontier:
            for desc, child in expand(psrc, macros if use_macros else None):
                h = sha(child.encode())
                if h not in scored:
                    scored.add(h)
                    gen.append((ppassed, psha, desc, child, h))
        room = exec_cap - execs
        if room <= 0:
            break
        gen = gen[:room]
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            reports = list(ex.map(lambda g: score(g[3].encode(), dev), gen))
        execs += len(gen)
        children = []
        for (ppassed, psha, desc, child, h), rep in zip(gen, reports):
            p = rep.get('passed', -1)
            history.append({'depth': d, 'parent': psha[:12], 'desc': desc, 'sha': h[:12],
                            'valid': rep.get('valid', False), 'passed': p})
            children.append((p, h, child))
            if use_macros and p > ppassed:
                m = extract_macro(desc)
                if m and m not in macros:
                    macros.append(m)
            if p > best_passed:
                best_passed, best_source = p, child
        children.sort(key=lambda t: (-t[0], t[1]))
        frontier = children[:width]
    return best_source, {'arm': 'beam-macro' if use_macros else 'beam', 'width': width,
                         'depth_cap': depth, 'execution_cap': exec_cap, 'executions': execs,
                         'macros': [list(m) for m in macros], 'best_dev_passed': best_passed,
                         'dev_total': total, 'trials': history}
