"""Graded dev fitness for the v10 challenger: value-distance between actual and
expected dev outputs, used as a tie-break below binary pass count. Rationale:
binary pass/fail gives no signal on neutral plateaus (v9 documented limit:
first_above). Distance is a heuristic shaping signal computed ONLY from dev
cases the proposer is allowed to see. Deterministic; no learned model.
"""
CAP_NUM = 100
MISMATCH = 10
PER_ITEM = 10

def _lev(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + (ca != cb)))
        prev = cur
    return min(prev[-1], CAP_NUM)

def distance(actual, expected):
    """Non-negative edit/value distance; 0 iff json-equal."""
    if expected is None or actual is None:
        return 0 if expected is None and actual is None else MISMATCH
    if isinstance(expected, bool) or isinstance(actual, bool):
        if type(actual) is not type(expected):
            return MISMATCH
        return 0 if actual == expected else MISMATCH
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return min(abs(actual - expected), CAP_NUM)
    if isinstance(expected, str) and isinstance(actual, str):
        return _lev(actual, expected)
    if isinstance(expected, list) and isinstance(actual, list):
        return PER_ITEM * abs(len(actual) - len(expected)) + sum(distance(a, e) for a, e in zip(actual, expected))
    if isinstance(expected, dict) and isinstance(actual, dict):
        extra = PER_ITEM * len(set(actual) ^ set(expected))
        return extra + sum(distance(actual[k], expected[k]) for k in set(actual) & set(expected))
    if type(actual) is not type(expected):
        return MISMATCH
    return 0 if actual == expected else MISMATCH

def fitness(report):
    """(passed desc, distance asc) key material from a score() report.
    Invalid candidates get worst fitness."""
    if not report.get('valid'):
        return (-1, 10 ** 9)
    return (report['passed'], sum(distance(c.get('actual'), c['expected']) for c in report['cases']))
