import copy
from itertools import combinations
from src.algorithm_components.helper_functions.minimum_self_distance_relation import get_minimum_self_distance_relations
from src.algorithm_components.helper_functions.helper_functions import fully_overlapping_partitions, not_fully_direct_connected_relation
from src.algorithm_components.helper_functions.partition_functions import merge_partitions, \
    add_partitions_with_no_start_or_end_to_arbitrary
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_concurrent


def detect_concurrent(log):
    return len(create_concurrent_partitions(log)) > 1

def get_concurrent_sublogs(log):
    partitions = create_concurrent_partitions(log)
    return create_sublogs_concurrent(log, partitions)

def create_concurrent_partitions(event_log):
    log = copy.deepcopy(event_log)
    directly_follows_relations = log.get_directly_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities_by_label()
    partitions = []

    #initialize partitions
    while activities:
        new_partition = [activities.pop()]
        partitions.append(new_partition)

    # connect partitions if 2 activities are never overlapping
    changed = True
    while changed:
        changed = False
        for p1, p2 in combinations(partitions, 2):
            if not fully_overlapping_partitions(p1, p2, overlapping_relations):
                merge_partitions(p1[0], p2[0], partitions)
                changed = True
                break

    # connect partitions if activities are not fully connected
    for relation in not_fully_direct_connected_relation(log.get_activities_by_label(), directly_follows_relations):
        merge_partitions(relation.get_first_activity(), relation.get_second_activity(), partitions)

    # connect partitions if activities are in minimum self distance relationship
    for relation in get_minimum_self_distance_relations(log):
        merge_partitions(relation.get_first_activity(), relation.get_second_activity(), partitions)

    # connect partition to arbitrary if it has no start or no end activity
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    partitions = add_partitions_with_no_start_or_end_to_arbitrary(partitions, start_activities, end_activities)

    return partitions