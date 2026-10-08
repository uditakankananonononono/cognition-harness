"""Fixed candidate executor. Receives inputs only, never expected answers."""
import json, resource, sys
resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
resource.setrlimit(resource.RLIMIT_AS, (134217728, 134217728))
resource.setrlimit(resource.RLIMIT_FSIZE, (65536, 65536))
resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
import candidate
cases = json.load(sys.stdin)
result = []
for case in cases:
    try:
        result.append({'id': case['id'], 'value': getattr(candidate, case['task'])(case['input'])})
    except Exception as exc:
        result.append({'id': case['id'], 'error': type(exc).__name__})
print(json.dumps(result, ensure_ascii=False))
