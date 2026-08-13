
from itertools import combinations

from src.algorithm_components.helper_functions.partition_functions import merge_partitions

def create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations):

    partitions = []
    for activity in activities:
        new_partition = set()
        new_partition.add(activity)
        partitions.append(new_partition)

    for a, b in combinations(activities, 2):
        # merge partitions if activities are overlapping in log
        if (a, b) in overlapping_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are pairwise reachable in log
        if (a, b) in eventually_follows_relations and (b, a) in eventually_follows_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are pairwise not-reachable in log
        if (a, b) not in eventually_follows_relations and (b, a) not in eventually_follows_relations:
            merge_partitions(a, b, partitions)
            # sort partitions (for sequence it's important)
            n = len(partitions)
        for i in range(n):
            a = next(iter(partitions[i]))
            for j in range(i + 1, n):
                b = next(iter(partitions[j]))
                if (a, b) not in eventually_follows_relations:
                    partitions[i], partitions[j] = partitions[j], partitions[i]

    return partitions