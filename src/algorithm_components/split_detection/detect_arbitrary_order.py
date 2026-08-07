import copy
from itertools import combinations
from src.algorithm_components.helper_functions.helper_functions import fully_eventually_connected_partitions
from src.algorithm_components.helper_functions.partition_functions import merge_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_sequential


def detect_arbitrary_order(log):
    return len(create_arbitrary_order_partitions(log)) > 1

def get_arbitrary_order_sublogs(log):
    partitions = create_arbitrary_order_partitions(log)
    return create_sublogs_sequential(log, partitions)

def create_arbitrary_order_partitions(event_log):
    log = copy.deepcopy(event_log)
    log_eventually_follows_relations = log.get_eventually_follows_relations()
    log_overlapping_relations =log.get_overlapping_relations()
    partitions = []
    activities = log.get_activities_by_label()

    while activities:
        new_partition = [activities.pop()]
        partitions.append(new_partition)

    # connect partitions if activities are overlapping in log
    for relation in log_overlapping_relations:
        merge_partitions(relation.get_first_activity(), relation.get_second_activity(), partitions)

    # connect partitions if activities are not fully eventually connected in log
    changed = True
    while changed:
        changed = False
        for p1, p2 in combinations(partitions, 2):
            if not fully_eventually_connected_partitions(p1, p2, log_eventually_follows_relations):
                merge_partitions(p1[0], p2[0], partitions)
                changed = True
                break

    # connect partitions if they are fully eventually connected in one trace
    for trace in log.get_traces():
        trace_eventually_follows_relations = trace.get_eventually_follows_relations()
        changed = True
        while changed:
            changed = False
            for p1, p2 in combinations(partitions, 2):
                if fully_eventually_connected_partitions(p1, p2, trace_eventually_follows_relations):
                    merge_partitions(p1[0], p2[0], partitions)
                    changed = True
                    break

    return partitions
