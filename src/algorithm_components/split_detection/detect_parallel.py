import copy
from itertools import combinations, product

from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation
from src.algorithm_components.helper_functions.partition_functions import merge_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_concurrent


def detect_parallel(log):
    return len(create_parallel_partitions(log)) > 1

def get_parallel_sublogs(log, parallel_partitions):
    return create_sublogs_concurrent(log, parallel_partitions)

def create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations):
    partitions = []

    #initialize partitions
    for activity in activities:
        new_partition = set()
        new_partition.add(activity)
        partitions.append(new_partition)

    # merge reachable partitions
    for a, b in combinations(activities, 2):
        if EventuallyFollowsRelation(a, b) in eventually_follows_relations or EventuallyFollowsRelation(b, a) in eventually_follows_relations:
            merge_partitions(a, b, partitions)
        if not OverlappingRelation(a, b) in overlapping_relations:
            merge_partitions(a, b, partitions)

    return partitions

