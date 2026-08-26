import copy
from itertools import combinations

from concurrency_miner_components.helper_functions.partition_functions import merge_partitions


def create_exclusive_choice_partitions(activities, overlapping_relations, eventually_follows_relations):
    # create partitions as sets with one activity each
    partitions = [{activity} for activity in activities]
    for a, b in combinations(activities, 2):
        # merge partitions if activities are overlapping in log
        if (a, b) in overlapping_relations or (b, a) in overlapping_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are reachable in log
        if (a, b) in eventually_follows_relations or (b, a) in eventually_follows_relations:
            merge_partitions(a, b, partitions)
    return partitions

def _create_exclusive_choice_partitions(event_log):
    log = copy.deepcopy(event_log)

    # create partitions as lists with one trace each
    partitions = [[trace] for trace in log]

    # Dictionary with trace to partition relationship
    trace_to_partition = {
        trace: partition
        for trace, partition in zip(log, partitions)
    }

    for t1, t2 in combinations(log, 2):
        if not t1.get_activities().isdisjoint(t2.get_activities()):
            p1 = trace_to_partition[t1]
            p2 = trace_to_partition[t2]

            if p1 is not p2:
                #combine partitions
                p1.extend(p2)

                #update dictionary
                for trace in p2:
                    trace_to_partition[trace] = p1

                partitions.remove(p2)

    return partitions