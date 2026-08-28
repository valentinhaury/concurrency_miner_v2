from itertools import combinations

from src.concurrency_miner_components.helper_functions.partition_functions import merge_partitions
from src.concurrency_miner_components.helper_functions.sublog_functions import create_sublogs_concurrent


def get_parallel_sublogs(log, parallel_partitions):
    return create_sublogs_concurrent(log, parallel_partitions)

def create_parallel_partitions(activities, overlapping_relations, eventually_follows_relation):

    #create partitions as sets with one activity each
    partitions = [{activity} for activity in activities]

    # merge non-fully overlapping partitions
    # -> if two activities are in a follows relation in any trace
    # or if they are never overlapping (because they can still be exclusive)
    for a, b in combinations(activities, 2):
        if (a, b) in eventually_follows_relation or (b, a) in eventually_follows_relation:
            merge_partitions(a, b, partitions)
        if (a, b) not in overlapping_relations and (b, a) not in overlapping_relations:
            merge_partitions(a, b, partitions)

    return partitions

