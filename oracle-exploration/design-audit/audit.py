"""Public exhaustive design calculation, not private evaluation or final scoring."""
import itertools
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ambiguity import evaluate


def audit():
    xs=list(range(-8,9))
    pool=[x for x in xs if x]
    result={'scope':'PUBLIC DESIGN AUDIT, not a frozen empirical study',
            'dev_domain':xs,'public_pool':pool,'rows':[]}
    for count in (1,2):
        blocks=[]
        for target in range(8):
            row={'target':target,'dev_count':count,'total':0,'ambiguous':0,
                 'one_query_ceiling':0,'adaptive_resolved':0,
                 'random_first_resolved_fraction_sum_numerator':0,
                 'random_first_resolved_fraction_sum_denominator_note':'use per-instance fractions below',
                 'instances':[]}
            for dev in itertools.combinations(xs,count):
                row['total']+=1
                space=[i for i in range(8) if all(evaluate(i,x)==evaluate(target,x) for x in dev)]
                if len(space)<2:continue
                row['ambiguous']+=1
                available=[x for x in pool if x not in dev]
                probes=[]
                for x in available:
                    outputs=[evaluate(i,x) for i in space]
                    groups=[outputs.count(y) for y in set(outputs)]
                    separated=(len(space)**2-sum(n*n for n in groups))//2
                    truth=evaluate(target,x)
                    resolves=sum(y==truth for y in outputs)==1
                    probes.append((x,separated,resolves))
                best=max(probes,key=lambda p:(p[1],-available.index(p[0])))
                # Fixed pool order here. Random-order expectation is mean over
                # all uniformly selected first inputs, not Monte Carlo trials.
                ceiling=any(p[2] for p in probes)
                adaptive=best[2] if best[1]>0 else False
                row['one_query_ceiling']+=ceiling
                row['adaptive_resolved']+=adaptive
                row['instances'].append({'dev_inputs':list(dev),'version_space':space,
                    'ceiling':ceiling,'adaptive_selected_input':best[0],
                    'adaptive_resolves':adaptive,'random_first_resolving_inputs':sum(p[2] for p in probes),
                    'random_first_available_inputs':len(probes)})
            blocks.append(row)
        result['rows'].extend(blocks)
    return result

if __name__=='__main__': print(json.dumps(audit(),indent=2))
