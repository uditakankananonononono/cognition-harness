"""Known finite DSL, charged development-label refinement. Not AGI/novelty evidence.

The caller-supplied oracle is an explicit trusted development-label provider, NOT
an evaluator final oracle. No network, files, eval or arbitrary source execution
is performed here. A malicious callback is not sandboxed by this module.
"""
import hashlib
import json

GRAMMAR = (('add', 1), ('add', -1), ('neg', 0), ('abs', 0),
           ('positive', 0), ('negative', 0), ('identity', 0), ('zero', 0))


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def evaluate(index, x):
    if type(index) is not int or not 0 <= index < len(GRAMMAR):
        raise ValueError('grammar_index')
    if type(x) is not int or not -32 <= x <= 32:
        raise ValueError('input_domain')
    op, arg = GRAMMAR[index]
    if op == 'add': return x + arg
    if op == 'neg': return -x
    if op == 'abs': return abs(x)
    if op == 'positive': return max(0, x)
    if op == 'negative': return min(0, x)
    if op == 'identity': return x
    return 0


def resolve(dev, pool, oracle, *, execution_cap=1024, query_cap=1, policy='adaptive'):
    """Select one known expression only after obtaining a consistent version space.

    Early singleton is returned without query; unresolved ambiguity yields no
    finalist, not a hidden complexity fallback. Caller explicitly provides oracle.
    Labels/callback outputs are visible development data, never final-case data.
    Query failures are charged, recorded, not retried. Total attempts <= query_cap.
    Logical caps do not bound callback time/memory/side effects or Python heap.
    """
    if policy not in ('adaptive', 'fixed'):
        raise ValueError('policy')
    if type(dev) is not list or not 1 <= len(dev) <= 16:
        raise ValueError('dev_shape')
    for pair in dev:
        if type(pair) is not list or len(pair) != 2:
            raise ValueError('dev_shape')
        if type(pair[0]) is not int or not -32 <= pair[0] <= 32 or type(pair[1]) is not int or not -64 <= pair[1] <= 64:
            raise ValueError('dev_domain')
    if len({pair[0] for pair in dev}) != len(dev):
        raise ValueError('duplicate_dev_inputs')
    if type(pool) is not list or not 0 <= len(pool) <= 65 or any(type(x) is not int or not -32 <= x <= 32 for x in pool):
        raise ValueError('pool_domain')
    if len(set(pool)) != len(pool):
        raise ValueError('duplicate_pool_inputs')
    if not callable(oracle):
        raise ValueError('oracle_required')
    if type(execution_cap) is not int or not 0 <= execution_cap <= 100000:
        raise ValueError('execution_cap')
    if type(query_cap) is not int or not 0 <= query_cap <= 8:
        raise ValueError('query_cap')
    config = {'schema': 'development-oracle-refinement-v1', 'grammar': GRAMMAR,
              'execution_cap': execution_cap, 'query_cap': query_cap,
              'pool_sha256': digest(pool), 'dev_sha256': digest(dev),
              'policy': policy,
              'selection': 'maximum separated pairs vs first unused pool index; both full-scan',
              'finalist': 'only singleton version space, no ranking fallback'}
    receipt = {'configuration': config, 'configuration_sha256': digest(config),
               'status': 'running', 'finalist': None, 'remaining_indices': [],
               'charged': {'generation': 0, 'dev_scalar': 0, 'probe_scalar': 0,
                           'pool_scan': 0, 'oracle_attempts': 0},
               'queries': [], 'rounds': [], 'correctness': 'not_final_scored'}
    used_inputs = {x for x, _ in dev}
    def scalar(index, x, category):
        if receipt['charged']['dev_scalar'] + receipt['charged']['probe_scalar'] >= execution_cap:
            raise RuntimeError('execution_cap_exhausted')
        receipt['charged'][category] += 1
        return evaluate(index, x)
    remaining = []
    try:
        for index in range(len(GRAMMAR)):
            receipt['charged']['generation'] += 1
            # Compute all dev observations; no short circuit hides useful cost.
            values = [scalar(index, x, 'dev_scalar') for x, _ in dev]
            if values == [y for _, y in dev]: remaining.append(index)
        while len(remaining) > 1:
            receipt['remaining_indices'] = list(remaining)
            if receipt['charged']['oracle_attempts'] >= query_cap:
                receipt['status'] = 'query_cap_ambiguous'; break
            scores, vectors = [], {}
            for pool_index, x in enumerate(pool):
                if x in used_inputs: continue
                receipt['charged']['pool_scan'] += 1
                values = [scalar(index, x, 'probe_scalar') for index in remaining]
                vectors[pool_index] = values
                counts = [values.count(y) for y in set(values)]
                # Number of unordered pairs whose predicted outputs differ.
                separated = (len(values)**2 - sum(n*n for n in counts)) // 2
                scores.append({'pool_index': pool_index, 'input': x, 'separated_pairs': separated})
            receipt['rounds'].append({'remaining_indices': list(remaining), 'scores': scores})
            if not scores or (policy == 'adaptive' and max(s['separated_pairs'] for s in scores) == 0):
                receipt['status'] = 'pool_cannot_separate'; break
            best = (max(scores, key=lambda s: (s['separated_pairs'], -s['pool_index']))
                    if policy == 'adaptive' else min(scores, key=lambda s: s['pool_index']))
            x = best['input']
            receipt['charged']['oracle_attempts'] += 1
            query = {'pool_index': best['pool_index'], 'input': x,
                     'before_indices': list(remaining), 'status': 'attempted'}
            receipt['queries'].append(query)
            try:
                answer = oracle(x)
            except Exception:
                # No exception text/secret/context is copied into the receipt.
                query['status'] = 'callback_failed'; receipt['status'] = 'oracle_failed'; break
            if type(answer) is not int or not -64 <= answer <= 64:
                query['status'] = 'invalid_label'; receipt['status'] = 'oracle_invalid'; break
            query.update(status='labeled', label=answer)
            used_inputs.add(x)
            remaining = [index for index, y in zip(remaining, vectors[best['pool_index']]) if y == answer]
            query['after_indices'] = list(remaining)
        else:
            if remaining:
                index = remaining[0]
                receipt.update(status='selected', finalist={'index': index, 'expression': GRAMMAR[index],
                                                            'sha256': digest(GRAMMAR[index])})
            else:
                receipt['status'] = 'no_consistent_candidate'
    except RuntimeError as error:
        if str(error) != 'execution_cap_exhausted': raise
        receipt['status'] = str(error)
    receipt['remaining_indices'] = list(remaining)
    receipt['unused_executions'] = execution_cap - receipt['charged']['dev_scalar'] - receipt['charged']['probe_scalar']
    receipt['unused_queries'] = query_cap - receipt['charged']['oracle_attempts']
    return receipt
