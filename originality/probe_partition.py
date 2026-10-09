"""Prototype of a known disagreement-partition mechanism, not novelty evidence."""
import hashlib,json

def split(candidates,probe_vectors,max_retained=16):
    # All evaluations occur outside this pure function; vectors contain no labels.
    if type(candidates)is not list or type(probe_vectors)is not dict or type(max_retained)is not int or max_retained<1:raise ValueError('shape')
    if len(candidates)>256:raise ValueError('candidate_limit')
    ids=[c['sha256']for c in candidates]
    if len(set(ids))!=len(ids)or any(type(i)is not str or len(i)!=64 for i in ids):raise ValueError('ids')
    if set(probe_vectors)!=set(ids):raise ValueError('missing_vector')
    lengths={len(v)for v in probe_vectors.values()}
    if len(lengths)!=1:raise ValueError('vector_length')
    count=next(iter(lengths),0)
    def typed(v):
        if v is None:return ['null',None]
        if type(v)is bool:return ['bool',v]
        if type(v)is int:return ['int',str(v)]
        if type(v)is str:return ['str',v]
        if type(v)is list:return ['list',[typed(x)for x in v]]
        raise ValueError('outside_probe_domain')
    def token(v):return json.dumps(typed(v),separators=(',',':'),ensure_ascii=False)
    scores=[len({token(probe_vectors[i][p])for i in ids})for p in range(count)]
    probe=max(range(count),key=lambda p:(scores[p],-p))if count else None
    buckets={}
    for c in candidates:
        key=token(probe_vectors[c['sha256']][probe])if probe is not None else 'no_probe'
        buckets.setdefault(key,[]).append(c['sha256'])
    groups=list(buckets.values());retained=[g[0]for g in groups][:max_retained]
    discarded=[i for i in ids if i not in retained]
    return {'selected_probe':probe,'distinct_output_counts':scores,'groups':groups,'retained':retained,'discarded':discarded,'cap_hit':len(groups)>max_retained,'correctness':'unknown','activation':'not_authorized'}
