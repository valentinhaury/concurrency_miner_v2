from itertools import combinations, permutations, product

from src.concurrency_miner_components.helper_functions.partition_functions import merge_partitions

def create_arbitrary_order_partitions(traces, activities, start_activities, end_activities, overlapping_relations, follows_relations, directly_follows_relations, minimum_self_distance_relations):
    # create partitions as sets with one activity each
    partitions = [{activity} for activity in activities]

    for a, b in combinations(activities, 2):
    # merge partitions if activities are overlapping in log
        if (a, b) in overlapping_relations or (b, a) in overlapping_relations:
            merge_partitions(a, b, partitions)

    #for a, b in combinations(activities, 2):
    # merge partitions if activities are not-fully pairwise reachable in log
        if (a, b) not in follows_relations or (b, a) not in follows_relations:
            merge_partitions(a, b, partitions)

    # merge partitions if activities are in minimum self distance relationship
        if (a, b) in minimum_self_distance_relations or (b, a) in minimum_self_distance_relations:
            merge_partitions(a, b, partitions)

    # TODO maybe do this following part multiple times until nothing changes anymore -> what to do with partitions that cant be merged that way

    def _connect_partitions_to_an_always_direct_connected_partition(this_partition):
        for candidate_partition in partitions:
            if not this_partition.isdisjoint(candidate_partition):
                continue
            always_direct_connected = True
            for t in traces:
                trace_directly_follows = t.get_directly_follows()
                trace_direct_connected = False
                for act1, act2 in product(this_partition, candidate_partition):
                    if (act1, act2) in trace_directly_follows or (act2, act1) in trace_directly_follows:
                        trace_direct_connected = True
                        break
                if not trace_direct_connected:
                    always_direct_connected = False
                    break
            if always_direct_connected:
                merge_partitions(next(iter(this_partition)), next(iter(candidate_partition)), partitions)
                return True
        return False

    def _merge_partitions_to_an_always_direct_connected_partition(partitions_to_merge):
        changed = True
        while changed:
            changed = False
            merged_partitions = []
            print("try to merge: ", str(partitions_to_merge), " to: ", str(partitions))
            for p in partitions_to_merge:
                if _connect_partitions_to_an_always_direct_connected_partition(p):
                    changed = True
                    merged_partitions.append(p)
            for merged_partition in merged_partitions:
                partitions_to_merge.remove(merged_partition)
        print("leftover: ", str(partitions_to_merge))

    # merge all partitions that either have no start or no end activities to a partition they are always connected to
    not_connected_to_start_or_end_partitions = []
    for partition in partitions:
        if partition.isdisjoint(start_activities) or partition.isdisjoint(end_activities):
            not_connected_to_start_or_end_partitions.append(partition)

    _merge_partitions_to_an_always_direct_connected_partition(not_connected_to_start_or_end_partitions)

    # merge all partitions that are not direct connected in both directions
    not_direct_connected_partitions = []
    for p1, p2 in combinations(partitions, 2):
        p1_p2 = False
        p2_p1 = False
        for a, b in product(p1, p2):
            if (a, b) in directly_follows_relations:
                p1_p2 = True
            if (b, a) in directly_follows_relations:
                p2_p1 = True
        if not p1_p2 or not p2_p1:
            not_direct_connected_partitions.append(p1)
            not_direct_connected_partitions.append(p2)

    _merge_partitions_to_an_always_direct_connected_partition(not_direct_connected_partitions)

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