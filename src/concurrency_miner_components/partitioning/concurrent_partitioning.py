from itertools import combinations

from src.concurrency_miner_components.helper_functions.partition_functions import merge_partitions
from src.concurrency_miner_components.helper_functions.sublog_functions import create_sublogs_concurrent


def get_concurrent_sublogs(log, concurrent_partitions):
    return create_sublogs_concurrent(log, concurrent_partitions)

def create_concurrent_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations, minimum_self_distance_relations):

    # create partitions as sets with one activity each
    partitions = [{activity} for activity in activities]

    for a, b in combinations(activities, 2):
        # merge partitions if activities are never overlapping in log
        if (a, b) not in overlapping_relations and (b, a) not in overlapping_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are not-fully pairwise connected in log
        if  (a, b) not in directly_follows_relations or (b, a) not in directly_follows_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are in minimum self distance relation in log
        if (a, b) in minimum_self_distance_relations or (b, a) in minimum_self_distance_relations:
            merge_partitions(a, b, partitions)

    # merge partitions with no start or no end activity to an arbitrary partition
    changed = True
    while len(partitions) > 1 and changed:
        changed = False
        for i, partition in enumerate(partitions):
            if partition.isdisjoint(start_activities) or partition.isdisjoint(end_activities):
                if i == 0:
                    merge_partitions(next(iter(partition)), next(iter(partitions[1])), partitions)
                else:
                    merge_partitions(next(iter(partition)), next(iter(partitions[0])), partitions)
                changed = True
                break
    return partitions