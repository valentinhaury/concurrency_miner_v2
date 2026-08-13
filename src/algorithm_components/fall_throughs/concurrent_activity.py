import copy

from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_concurrent
from src.algorithm_components.partitioning.detect_arbitrary_order import create_arbitrary_order_partitions
from src.algorithm_components.partitioning.concurrent_partitioning import create_concurrent_partitions
from src.algorithm_components.partitioning.exclusive_choice_partitioning import create_exclusive_choice_partitions
from src.algorithm_components.partitioning.interleaving_partitioning import create_interleaving_partitions
from src.algorithm_components.partitioning.detect_loop import create_loop_partitions
from src.algorithm_components.partitioning.detect_parallel import create_parallel_partitions
from src.algorithm_components.partitioning.sequence_partitioning import create_sequence_partitions

def get_concurrent_activity_sublogs(log, concurrent_partitions):
    return create_sublogs_concurrent(log, concurrent_partitions)

def get_concurrent_activity_partitions(event_log, activities):
    log = copy.deepcopy(event_log)
    for activity in activities:
        activity_set = set()
        activity_set.add(activity)
        set_without_activity = activities - activity_set
        sublogs = create_sublogs_concurrent(log, [activity_set, set_without_activity])
        for sublog in sublogs:
            if not activity in sublog.get_activities():
                if split_found(sublog):
                    return [activity_set, set_without_activity]
    return []

def split_found(log):

    traces = log.get_traces()
    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    eventually_follows_relations = log.get_eventually_follows_relations()
    directly_follows_relations = log.get_directly_follows_relations()
    minimum_self_distance_relations = log.get_minimum_self_distance_relations()

    exclusive_choice_partitions = create_exclusive_choice_partitions(log)
    if len(exclusive_choice_partitions) > 1:
        return True
    sequence_partitions = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)
    if len(sequence_partitions) > 1:
        return True
    arbitrary_order_partitions = create_arbitrary_order_partitions(traces, activities, start_activities, end_activities, overlapping_relations, eventually_follows_relations, directly_follows_relations)
    if len(arbitrary_order_partitions) > 1:
        return True
    interleaving_partitions = create_interleaving_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations, minimum_self_distance_relations)
    if len(interleaving_partitions) > 1:
        return True
    concurrent_partitions = create_concurrent_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations, minimum_self_distance_relations)
    if len(concurrent_partitions) > 1:
        return True
    parallel_partitions = create_parallel_partitions(activities, eventually_follows_relations)
    if len(parallel_partitions) > 1:
        return True
    loop_partitions = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)
    if len(loop_partitions) > 1:
        return True
    return False
