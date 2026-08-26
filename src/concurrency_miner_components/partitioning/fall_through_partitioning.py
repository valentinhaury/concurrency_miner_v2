import copy
from datetime import datetime
from itertools import permutations

from concurrency_miner_components.helper_functions.compute_minimum_self_distance_relation import \
    compute_minimum_self_distance_relations
from concurrency_miner_components.helper_functions.sublog_functions import create_sublogs_concurrent
from concurrency_miner_components.partitioning.concurrent_partitioning import create_concurrent_partitions
from concurrency_miner_components.partitioning.arbitrary_order_partitioning import create_arbitrary_order_partitions
from concurrency_miner_components.partitioning.exclusive_choice_partitioning import create_exclusive_choice_partitions
from concurrency_miner_components.partitioning.interleaving_partitioning import create_interleaving_partitions
from concurrency_miner_components.partitioning.loop_partitioning import create_loop_partitions
from concurrency_miner_components.partitioning.parallel_partitioning import create_parallel_partitions
from concurrency_miner_components.partitioning.sequence_partitioning import create_sequence_partitions

# Flower model - every activity gets its own sub-log
def create_flower_model_partitions(activities):
    partitions = []
    for activity in activities:
        partitions.append({activity})
    return partitions

# an activity that is in every trace gets put concurrent to the rest
def create_activity_once_per_trace_partitions(traces, activities):
    activities_in_every_trace = set()
    activities_in_every_trace |= traces[0].get_activities()
    for trace in traces:
        activities_in_every_trace &= trace.activities

    if activities_in_every_trace:
        partition1 = set()
        partition1.add(next(iter(activities_in_every_trace)))
        partition2 = set(activities - partition1)
        return [partition1, partition2]
    else:
        return [activities]

# for every activity it trys if a split can be found if that activity is put concurrent to the rest.
#TODO make it run task parallel
def get_concurrent_activity_partitions(event_log, activities):
    log = copy.deepcopy(event_log)
    for activity in activities:
        print("activity: ", activity)
        activity_set = set()
        activity_set.add(activity)
        set_without_activity = activities - activity_set
        sublogs = create_sublogs_concurrent(log, [activity_set, set_without_activity])
        if _split_found(sublogs[1]):
            return [activity_set, set_without_activity]
    return []

def _split_found(log):
    # initiate log parameters
    log_activities = set()  # contains all activities, activities are always represented by their name-string
    log_start_activities = set()  # contains all start activities
    log_end_activities = set()  # contains all end activities
    log_overlapping_relation = set()  # contains pairs of activities that occur parallel at least once in the log
    log_directly_follows = set()  # contains pairs of activities where the second follows at least once directly after the first in the trace
    log_eventually_follows = set()  # contains the transitive closure of the directly follows relation
    log_minimum_self_distance = set()  # contains pairs of activities where the second one is a witness of the minimum self distance relationship of the first

    for trace in log:
        log_activities |= trace.get_activities()
        log_start_activities |= trace.get_start_activities()
        log_end_activities |= trace.get_end_activities()
        log_overlapping_relation |= trace.get_overlapping_activities()
        log_directly_follows |= trace.get_directly_follows()

    # create the transitive closure of the directly follows relation of the log
    log_eventually_follows |= copy.copy(log_directly_follows)
    for r1, r2 in permutations(log_directly_follows, 2):
        if r1[1] == r2[0]:
            log_eventually_follows.add((r1[0], r2[1]))

    log_minimum_self_distance |= compute_minimum_self_distance_relations(log_activities, log)

    exclusive_choice_partitions = create_exclusive_choice_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(exclusive_choice_partitions) > 1:
        return True
    sequence_partitions = create_sequence_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(sequence_partitions) > 1:
        return True
    arbitrary_order_partitions = create_arbitrary_order_partitions(log, log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_eventually_follows, log_directly_follows)
    if len(arbitrary_order_partitions) > 1:
        return True
    interleaving_partitions = create_interleaving_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_minimum_self_distance)
    if len(interleaving_partitions) > 1:
        return True
    concurrent_partitions = create_concurrent_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_minimum_self_distance)
    if len(concurrent_partitions) > 1:
        return True
    parallel_partitions = create_parallel_partitions(log_activities, log_eventually_follows)
    if len(parallel_partitions) > 1:
        return True
    loop_partitions = create_loop_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows)
    if len(loop_partitions) > 1:
        return True
    return False

