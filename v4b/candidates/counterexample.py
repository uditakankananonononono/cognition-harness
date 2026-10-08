def arithmetic(tree):
    if type(tree) is int:
        return tree
    left = arithmetic(tree[1])
    right = arithmetic(tree[2])
    if tree[0] == '+':
        return left + right
    if tree[0] == '-':
        return left - right
    return left * right

def first_index(data):
    (values, target) = data
    if not values:
        return 0
    return next((i for (i, v) in enumerate(values) if v == target), -1)
