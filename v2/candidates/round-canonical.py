def canonical(text):
    return text.lower().split()

def unique(items):
    return sorted(set(items))

def merge(intervals):
    out = []
    for (start, end) in sorted(intervals):
        if out and start < out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return out
