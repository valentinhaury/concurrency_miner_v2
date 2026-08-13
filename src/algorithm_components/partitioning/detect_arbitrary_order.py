from itertools import combinations, permutations, product

from src.data_structures.relations.relation import Relation
from src.data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from src.data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation
from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.data_structures.relations.strict_partial_order import StrictPartialOrder
from src.algorithm_components.helper_functions.partition_functions import merge_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_sequential


def get_arbitrary_order_sublogs(log, arbitrary_order_partitions):
    return create_sublogs_sequential(log, arbitrary_order_partitions)

def create_arbitrary_order_partitions(traces, activities, start_activities, end_activities, overlapping_relations, eventually_follows_relations, directly_follows_relations):
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

    # merge all partitions that either have no start or no end activities
    changed = True
    while len(partitions) > 1 and changed:
        changed = False
        for p1, p2 in combinations(partitions, 2):
            if p1.isdisjoint(start_activities) and p2.isdisjoint(start_activities):
                merge_partitions(next(iter(p1)), next(iter(p2)), partitions)
                changed = True
                break
            if p1.isdisjoint(end_activities) and p2.isdisjoint(end_activities):
                merge_partitions(next(iter(p1)), next(iter(p2)), partitions)
                changed = True
                break
    for p1, p2 in permutations(partitions, 2):
        if p1.isdisjoint(start_activities) and p2.isdisjoint(end_activities):
            merge_partitions(next(iter(p1)), next(iter(p2)), partitions)
            break

    # merge all partitions that are not direct connected in both directions
    not_direct_connected = []
    for p1, p2 in combinations(partitions, 2):
            p1_p2 = False
            p2_p1 = False
            for a, b in product(p1, p2):
                if DirectlyFollowsRelation(a, b) in directly_follows_relations:
                    p1_p2 = True
                if DirectlyFollowsRelation(b, a) in directly_follows_relations:
                    p2_p1 = True
            if not p1_p2 or not p2_p1:
                not_direct_connected.append(Relation(p1, p2))

    for relation in not_direct_connected:
        merge_partitions(next(iter(relation.get_first())), next(iter(relation.get_second())), partitions)

    # merge partitions if partitions are pairwise reachable in one trace
    for trace in traces:
        for e1, e2, e3 in permutations(trace.get_events(), 3):
            if not StrictPartialOrder(e1, e2) in trace.get_strict_partial_order() or not StrictPartialOrder(e2, e3) in trace.get_strict_partial_order():
                continue
            for partition in partitions:
                if e1.get_label() in partition and e3.get_label() in partition:
                    merge_partitions(e1.get_label(), e2.get_label(), partitions)
                    break

    return partitions