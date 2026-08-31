from itertools import combinations, permutations, product

from src.concurrency_miner_components.helper_functions.partition_functions import merge_partitions
from src.concurrency_miner_components.helper_functions.sublog_functions import create_sublogs_sequential


def get_arbitrary_order_sublogs(log, arbitrary_order_partitions):
    return create_sublogs_sequential(log, arbitrary_order_partitions)

def create_arbitrary_order_partitions(traces, activities, start_activities, end_activities, overlapping_relations, eventually_follows_relations, directly_follows_relations, minimum_self_distance_relations):
    # create partitions as sets with one activity each
    partitions = [{activity} for activity in activities]

    for a, b in combinations(activities, 2):
    # merge partitions if activities are overlapping in log
        if (a, b) in overlapping_relations or (b, a) in overlapping_relations:
            merge_partitions(a, b, partitions)

    #for a, b in combinations(activities, 2):
    # merge partitions if activities are not-fully pairwise reachable in log
        if (a, b) not in eventually_follows_relations or (b, a) not in eventually_follows_relations:
            merge_partitions(a, b, partitions)

    # merge partitions if activities are in minimum self distance relationship
        if (a, b) in minimum_self_distance_relations or (b, a) in minimum_self_distance_relations:
            merge_partitions(a, b, partitions)



    # merge all partitions that either have no start or no end activities to a partition they are always connected to
    partitions_to_merge = []
    for partition in partitions:
        if partition.isdisjoint(start_activities) or partition.isdisjoint(end_activities):
            partitions_to_merge.append(partition)
    # TODO maybe do this following part multiple times until nothing changes anymore
    connect_partitions_relation = []
    for p1, p2 in product(partitions_to_merge, partitions):
        if p1 != p2:
            always_direct_connected = True
            for trace in traces:
                trace_directly_follows = trace.get_directly_follows()
                trace_direct_connected = False
                for a1, a2 in product(p1, p2):
                    if (a1, a2) in trace_directly_follows or (a2, a1) in trace_directly_follows:
                        trace_direct_connected = True
                        break
                if not trace_direct_connected:
                    always_direct_connected = False
                    break
            if always_direct_connected:
                connect_partitions_relation.append((p1, p2))
    for relation in connect_partitions_relation:
        merge_partitions(next(iter(relation[0])), next(iter(relation[1])), partitions)

    # merge all partitions that are not direct connected in both directions
    # TODO maybe merge them to partitions they are always connected to like with the start or end activities
    if False:
        not_direct_connected = []
        for p1, p2 in combinations(partitions, 2):
                p1_p2 = False
                p2_p1 = False
                for a, b in product(p1, p2):
                    if (a, b) in directly_follows_relations:
                        p1_p2 = True
                    if (b, a) in directly_follows_relations:
                        p2_p1 = True
                if not p1_p2 or not p2_p1:
                    not_direct_connected.append((p1, p2))

        for relation in not_direct_connected:
            merge_partitions(next(iter(relation[0])), next(iter(relation[1])), partitions)

    # merge partitions if partitions are pairwise reachable in one trace
    for trace in traces:
        trace_eventually_follows = trace.get_eventually_follows()
        for a1, a2, a3 in permutations(trace.activities, 3):
            if not (a1, a2) in trace_eventually_follows or not (a2, a3) in trace_eventually_follows:
                continue
            for partition in partitions:
                if a1 in partition and a3 in partition:
                    merge_partitions(a1, a2, partitions)
                    break

    return partitions