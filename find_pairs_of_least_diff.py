def find_min_diff_pairs(arr):
    if len(arr) < 2:
        return []

    # Step 1: Sort the array
    arr.sort()

    # Step 2: Find the minimum difference
    min_diff = float('inf')
    pairs = []

    for i in range(len(arr) - 1):
        diff = arr[i + 1] - arr[i]
        if diff < min_diff:
            min_diff = diff
            pairs = [(arr[i], arr[i + 1])]
        elif diff == min_diff:
            pairs.append((arr[i], arr[i + 1]))

    return pairs

if __init__ == 'main':
  arr = [2, 4, 1, 3, 10, 6]
  find_min_diff_pairs(arr)
