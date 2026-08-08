import copy
from itertools import combinations, permutations

from src.data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation
from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.data_structures.relations.strict_partial_order import StrictPartialOrder
from src.algorithm_components.helper_functions.partition_functions import merge_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_sequential


def detect_arbitrary_order(log):
    return len(create_arbitrary_order_partitions(log)) > 1

def get_arbitrary_order_sublogs(log, arbitrary_order_partitions):
    return create_sublogs_sequential(log, arbitrary_order_partitions)

def create_arbitrary_order_partitions(traces, activities, overlapping_relations, eventually_follows_relations):
    partitions = []
    for activity in activities:
        new_partition = set()
        new_partition.add(activity)
        partitions.append(new_partition)

    for a, b in combinations(activities, 2):
        # merge partitions if activities are overlapping in log
        if OverlappingRelation(a, b) in overlapping_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are not-fully pairwise reachable in log
        if (not EventuallyFollowsRelation(a, b) in eventually_follows_relations) or (not EventuallyFollowsRelation(b, a) in eventually_follows_relations):
            merge_partitions(a, b, partitions)

        # merge partitions if partitions are pairwise reachable in one trace
    for trace in traces:
        for e1, e2, e3 in permutations(trace.get_events(), 3):
            if not StrictPartialOrder(e1, e2) in trace.get_strict_partial_order() or not StrictPartialOrder(e2, e3) in trace.get_strict_partial_order():
                continue
            for partition in partitions:
                if e1.get_activity() in partition and e3.get_activity() in partition:
                    merge_partitions(e1.get_activity(), e2.get_activity(), partitions)
                    break

    return partitions
