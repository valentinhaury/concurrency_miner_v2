from itertools import combinations

from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.algorithm_components.helper_functions.partition_functions import merge_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_concurrent


def detect_parallel(log):
    return len(create_parallel_partitions(log)) > 1

def get_parallel_sublogs(log, parallel_partitions):
    return create_sublogs_concurrent(log, parallel_partitions)

def create_parallel_partitions(traces, activities):
    partitions = []

    #initialize partitions
    for activity in activities:
        new_partition = set()
        new_partition.add(activity)
        partitions.append(new_partition)

    # merge non-fully overlapping partitions
    for a, b in combinations(activities, 2):
        for trace in traces:
            if not OverlappingRelation(a, b) in trace.get_overlapping_relations_trace():
                merge_partitions(a, b, partitions)
                break

    return partitions

