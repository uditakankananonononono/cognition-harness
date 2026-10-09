"""Finite integer DSL study plumbing. No arbitrary source execution or final scoring.

Public, developer-known operators only. Unit-test fixtures are not unseen tasks.
A cap exit returns no finalist. Counts report actual charged work, not useful work.
"""
import hashlib
import json
from pathlib import Path
from retention_ledger import create, transition, encode
from probe_partition import split

METHODS = ('first', 'fixed', 'disagreement')
# Frozen ordering proposal deliberately differs from complexity ordering.
GRAMMAR = (('add', 1), ('add', -1), ('neg', 0), ('abs', 0),
           ('positive', 0), ('negative', 0), ('identity', 0), ('zero', 0))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def source(candidate):
    return canonical(candidate).decode()


def interpret(candidate, x):
    if type(x) is not int or not -32 <= x <= 32:
        raise ValueError('input_domain')
    op, arg = candidate
    if op == 'add': return x + arg
    if op == 'neg': return -x
    if op == 'abs': return abs(x)
    if op == 'positive': return max(0, x)
    if op == 'negative': return min(0, x)
    if op == 'identity': return x
    if op == 'zero': return 0
    raise ValueError('operator')


def load_pool(path):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    if type(data) is not dict or set(data) != {'schema', 'inputs'} or data['schema'] != 'integer-public-probes-v1':
        raise ValueError('pool_shape')
    xs = data['inputs']
    if type(xs) is not list or not 1 <= len(xs) <= 32 or any(type(x) is not int or not -32 <= x <= 32 for x in xs) or len(set(xs)) != len(xs):
        raise ValueError('pool_domain')
    return xs, hashlib.sha256(raw).hexdigest()


def run(method, dev, pool_path, expected_pool_hash, execution_cap=1024, byte_cap=32768, k=4):
    if method not in METHODS: raise ValueError('method')
    if type(execution_cap) is not int or not 0 <= execution_cap <= 100000: raise ValueError('execution_cap')
    if type(k) is not int or not 1 <= k <= 8: raise ValueError('k')
    if type(dev) is not list or not 1 <= len(dev) <= 16: raise ValueError('dev_shape')
    for pair in dev:
        if type(pair) is not list or len(pair) != 2 or any(type(v) is not int for v in pair) or not -32 <= pair[0] <= 32 or not -64 <= pair[1] <= 64:
            raise ValueError('dev_domain')
    pool, pool_hash = load_pool(pool_path)
    if pool_hash != expected_pool_hash: raise ValueError('pool_pin')
    protocol = {'grammar': GRAMMAR, 'k': k, 'execution_cap': execution_cap,
                'byte_cap': byte_cap, 'pool_sha256': pool_hash,
                'finalist': 'minimum development mismatches, then expression complexity, then grammar index'}
    pin = hashlib.sha256(canonical(protocol)).hexdigest()
    ledger = create(pin, byte_cap)
    receipt = {'method': method, 'configuration_sha256': pin, 'pool_sha256': pool_hash,
               'charged': {'generation': 0, 'dev_scalar': 0, 'probe_scalar': 0, 'pool_scan': 0},
               'execution_cap': execution_cap, 'byte_cap': byte_cap, 'status': 'running',
               'finalist': None, 'correctness': 'not_scored', 'ledger': None}
    def evaluate(candidate, x, category):
        total = receipt['charged']['dev_scalar'] + receipt['charged']['probe_scalar']
        if total >= execution_cap: raise ValueError('execution_cap_exhausted')
        receipt['charged'][category] += 1
        return interpret(candidate, x)
    candidates, vectors, probes, buckets = [], {}, {}, {}
    try:
        for index, candidate in enumerate(GRAMMAR):
            receipt['charged']['generation'] += 1
            text = source(candidate); key = hashlib.sha256(text.encode()).hexdigest()
            ledger = transition(ledger, 'retain', text, 'grammar index %d' % index)
            item = {'sha256': key, 'index': index, 'expression': candidate}
            candidates.append(item)
            values = [evaluate(candidate, x, 'dev_scalar') for x, _ in dev]
            vectors[key] = values
            # Every method pays for the identical full public pool, even if unused.
            probes[key] = []
            for x in pool:
                receipt['charged']['pool_scan'] += 1
                probes[key].append(evaluate(candidate, x, 'probe_scalar'))
            buckets.setdefault(tuple(values), []).append(item)
        retained = []
        for bucket_id, group in enumerate(buckets.values()):
            if method == 'first': chosen = [group[0]['sha256']]
            elif method == 'fixed': chosen = [c['sha256'] for c in group[:k]]
            else:
                ids = {c['sha256'] for c in group}
                chosen = split(group, {i: probes[i] for i in ids}, k)['retained']
            for item in group[1:]:
                ledger = transition(ledger, 'prune', item['sha256'], 'dev collision bucket %d' % bucket_id)
            for item in group:
                key = item['sha256']
                if key in chosen:
                    if item != group[0]:
                        ledger = transition(ledger, 'restore', key, '%s public pool %s bucket %d' % (method, pool_hash, bucket_id))
                    retained.append(item)
                elif item == group[0]:
                    ledger = transition(ledger, 'prune', key, 'selection cap bucket %d' % bucket_id)
        def rank(item):
            key = item['sha256']; op = item['expression'][0]
            complexity = 0 if op in ('identity', 'zero') else 1
            return (sum(a != pair[1] for a, pair in zip(vectors[key], dev)), complexity, item['index'])
        winner = min(retained, key=rank)
        receipt.update(status='selected', finalist={'sha256': winner['sha256'],
                       'expression': winner['expression'], 'ranking': rank(winner)},
                       selection_sha256=[c['sha256'] for c in retained])
    except ValueError as error:
        if str(error) not in ('execution_cap_exhausted', 'byte_budget_exhausted'): raise
        receipt['status'] = str(error)
    receipt['ledger'] = ledger
    receipt['charged']['ledger_bytes'] = len(encode(ledger))
    receipt['unused_executions'] = execution_cap - receipt['charged']['dev_scalar'] - receipt['charged']['probe_scalar']
    return receipt
