def arithmetic(tree):
    if type(tree) is int:
        return tree
    left = arithmetic(tree[1])
    right = arithmetic(tree[2])
    if tree[0] == '+':
        return left + right
    if tree[0] == '-':
        return left + right
    return left + right

def first_index(data):
    values, target = data
    lo = 0
    hi = len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    if lo < len(values) and values[lo] == target:
        return lo
    return -1
