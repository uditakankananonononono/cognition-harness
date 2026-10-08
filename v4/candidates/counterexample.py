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
    return 0 if data[0] else -1
