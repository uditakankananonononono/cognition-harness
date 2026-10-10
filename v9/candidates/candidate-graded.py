def clamp_range(values):
    (x, lo, hi) = values
    return min(max(x, lo), hi)

def second_largest(nums):
    return sorted(set(nums))[-2]

def count_even(nums):
    return sum((1 for n in nums if n % 2 < 1))

def running_max(nums):
    out = []
    m = nums[0]
    for n in nums:
        m = max(m, n)
        out.append(m)
    return out

def first_above(pair):
    (values, limit) = pair
    for v in values:
        if v >= limit:
            return v
    return None