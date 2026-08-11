from itertools import combinations

from concurrency_miner_cortado.helper_functions.merge_partitions import merge_partitions


def compute_arbitrary_order_partitions(traces, activities,
                                    start_activities, end_activities,
                                concurrency_pairs, follows, directly_follows):
    partitions = [{activity} for activity in activities]

    for a, b in combinations(activities, 2):
        # merge partitions if activities are overlapping in log
        if (a, b) in concurrency_pairs:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are not-fully pairwise reachable in log
        if (a, b) not in follows or (b, a) not in follows:
            merge_partitions(a, b, partitions)
