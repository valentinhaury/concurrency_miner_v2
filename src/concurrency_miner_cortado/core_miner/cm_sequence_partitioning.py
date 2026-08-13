from itertools import combinations

from algorithm_components.helper_functions.partition_functions import merge_partitions

def compute_sequence_partitions(activities, concurrency_pairs, follows):
    partitions = [{activity} for activity in activities]
    for a, b in combinations(activities, 2):
    # merge partitions if activities are overlapping in log
        if (a, b) in concurrency_pairs:
            merge_partitions(a, b, partitions)
    # merge partitions if activities are pairwise reachable in log
        if (a, b) in follows and (b, a) in follows:
            merge_partitions(a, b, partitions)
    # merge partitions if activities are pairwise not-reachable in log
        if (a, b) not in follows and (b, a) not in follows:
            merge_partitions(a, b, partitions)
    # sort partitions (for sequence it's important)
    n = len(partitions)
    for i in range(n):
        a = next(iter(partitions[i]))
        for j in range(i + 1, n):
            b = next(iter(partitions[j]))
            if (a, b) not in follows:
                partitions[i], partitions[j] = partitions[j], partitions[i]

    return partitions