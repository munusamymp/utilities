import random

def quickselect(nums, k):
    if not nums:
        return None

    pivot = random.choice(nums)

    left = [x for x in nums if x > pivot]
    mid = [x for x in nums if x == pivot]
    right = [x for x in nums if x < pivot]

    L, M = len(left), len(mid)

    if k <= L:
        return quickselect(left, k)
    elif k <= L + M:
        return pivot
    else:
        return quickselect(right, k - L - M)
