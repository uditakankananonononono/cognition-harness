"""Bounded local source/decision receipt. Integrity checks, not authentication.

No execution, oracle, network, promotion, durable store, or evaluator-pack access.
The byte limit covers the entire canonical UTF-8 JSON receipt, including sources,
metadata and events. Failing transitions leave prior state unchanged.
"""
import copy
import hashlib
import json
import re

SCHEMA = 'source-retention-ledger-v1'
HEX = re.compile(r'^[0-9a-f]{64}$')


def digest(source):
    if type(source) is not str:
        raise ValueError('source_type')
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def encode(state):
    return json.dumps(state, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def bounded(state):
    if len(encode(state)) > state['max_bytes']:
        raise ValueError('byte_budget_exhausted')
    return state


def create(protocol_sha256, max_bytes):
    if type(protocol_sha256) is not str or not HEX.fullmatch(protocol_sha256):
        raise ValueError('protocol_hash')
    if type(max_bytes) is not int or not 1 <= max_bytes <= 1_000_000:
        raise ValueError('byte_budget')
    return bounded({'schema': SCHEMA, 'protocol_sha256': protocol_sha256,
                    'max_bytes': max_bytes, 'sources': {}, 'events': []})


def validate(state):
    if type(state) is not dict or set(state) != {
            'schema', 'protocol_sha256', 'max_bytes', 'sources', 'events'}:
        raise ValueError('state_shape')
    create(state['protocol_sha256'], state['max_bytes'])
    if state['schema'] != SCHEMA or type(state['sources']) is not dict or type(state['events']) is not list:
        raise ValueError('state_schema')
    if len(state['sources']) > 256:
        raise ValueError('source_limit')
    for key, record in state['sources'].items():
        if type(record) is not dict or set(record) != {'source', 'status'}:
            raise ValueError('record_shape')
        if digest(record['source']) != key or record['status'] not in ('available', 'pruned', 'restored'):
            raise ValueError('record_integrity')
    # Rebuild events to check local state consistency, including retained bytes.
    replay = create(state['protocol_sha256'], state['max_bytes'])
    for event in state['events']:
        if type(event) is not dict or set(event) != {'seq', 'kind', 'source_sha256', 'reason'}:
            raise ValueError('event_shape')
        if type(event['seq']) is not int or event['seq'] != len(replay['events']):
            raise ValueError('event_order')
        key = event['source_sha256']
        if key not in state['sources']:
            raise ValueError('unknown_source')
        kind = event['kind']
        if kind == 'retain':
            if key in replay['sources']:
                raise ValueError('duplicate_retain')
            replay['sources'][key] = {'source': state['sources'][key]['source'], 'status': 'available'}
        elif kind in ('prune', 'restore'):
            expected = ('available', 'restored') if kind == 'prune' else ('pruned',)
            if key not in replay['sources'] or replay['sources'][key]['status'] not in expected:
                raise ValueError('invalid_transition')
            replay['sources'][key]['status'] = 'pruned' if kind == 'prune' else 'restored'
        else:
            raise ValueError('event_kind')
        if type(event['reason']) is not str or not event['reason'] or len(event['reason'].encode('utf-8')) > 512:
            raise ValueError('reason')
        replay['events'].append(copy.deepcopy(event))
    if replay != state:
        raise ValueError('state_event_mismatch')
    return bounded(state)


def transition(state, kind, source_or_hash, reason):
    validate(state)
    new = copy.deepcopy(state)
    if type(reason) is not str or not reason or len(reason.encode('utf-8')) > 512:
        raise ValueError('reason')
    if kind == 'retain':
        key = digest(source_or_hash)
        if key in new['sources']:
            raise ValueError('duplicate_retain')
        if len(new['sources']) >= 256:
            raise ValueError('source_limit')
        new['sources'][key] = {'source': source_or_hash, 'status': 'available'}
    elif kind in ('prune', 'restore'):
        key = source_or_hash
        if type(key) is not str or key not in new['sources']:
            raise ValueError('unknown_source')
        expected = ('available', 'restored') if kind == 'prune' else ('pruned',)
        if new['sources'][key]['status'] not in expected:
            raise ValueError('invalid_transition')
        new['sources'][key]['status'] = 'pruned' if kind == 'prune' else 'restored'
    else:
        raise ValueError('event_kind')
    new['events'].append({'seq': len(new['events']), 'kind': kind,
                          'source_sha256': key, 'reason': reason})
    return bounded(new)


def restored_source(state, source_sha256):
    validate(state)
    record = state['sources'].get(source_sha256)
    if record is None or record['status'] != 'restored':
        raise ValueError('not_restored')
    return record['source']
