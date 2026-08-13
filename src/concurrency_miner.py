import copy
from datetime import datetime
from itertools import permutations

from algorithm_components.fall_throughs.concurrent_activity import get_concurrent_activity_partitions, \
    get_concurrent_activity_sublogs
from algorithm_components.fall_throughs.flower_model import create_flower_model_partitions, get_flower_model_sublogs
from algorithm_components.partitioning.detect_loop import create_loop_partitions
from algorithm_components.fall_throughs.activitiy_once_per_trace import create_activity_once_per_trace_partitions, \
    get_activity_once_per_trace_sublogs
from data_structures.trace import Trace
from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node
from src.algorithm_components.partitioning.detect_arbitrary_order import get_arbitrary_order_sublogs, create_arbitrary_order_partitions
from algorithm_components.helper_functions.sublog_functions import get_loop_sublogs, create_sublogs_sequential
from src.algorithm_components.partitioning.detect_parallel import get_parallel_sublogs, create_parallel_partitions
from src.algorithm_components.partitioning.detect_concurrent import get_concurrent_sublogs, create_concurrent_partitions
from src.algorithm_components.partitioning.detect_interleaving import create_interleaving_partitions, get_interleaving_sublogs
from src.algorithm_components.partitioning.detect_exclusive import create_exclusive_choice_partitions
from src.algorithm_components.partitioning.detect_sequence import create_sequence_partitions



def concurrency_miner(
        event_log: list[Trace]
):

# handle empty log
    if not event_log:
        return Node("tau")

# handle empty traces
    log = [Trace({"tau"}, {}) if len(old_trace.get_events()) == 0 else old_trace for old_trace in event_log]

    print(f"[{datetime.now():%H:%M:%S}] Empty Traces")

# initiate log parameters
    log_activities = set()
    log_start_activities = set()
    log_end_activities = set()
    log_concurrency_pairs = set()
    log_directly_follows = set()

    for trace in log:
        log_activities |= trace.get_events()
        log_start_activities |= trace.get_start_activities()
        log_end_activities |= trace.get_end_activities()
        log_concurrency_pairs |= trace.get_overlapping_relations_trace()
        log_directly_follows |= trace.get_directly_follows()

    print(f"[{datetime.now():%H:%M:%S}] Initiated Log")

    # create the transitive closure of the directly follows relation of the log
    log_eventually_follows = copy.copy(log_directly_follows)
    for r1, r2 in permutations(log_directly_follows, 2):
        if r1[1] == r2[0]:
            log_eventually_follows.add((r1[0], r2[1]))

    print(f"[{datetime.now():%H:%M:%S}] Initiated log transitiv closure")

##### BASE CASES
# end recursion and add a single activity node, a self_loop node and/or a multi_instance node
    if len(log_activities) < 2:
        single_activity = (next(iter(log_activities)), next(iter(log_activities)))
        if not log_concurrency_pairs and not log_directly_follows:
            process_tree = Node(single_activity)
            return process_tree
        single_activity_pair = (single_activity, single_activity)
        if single_activity_pair in log_concurrency_pairs and single_activity_pair not in log_directly_follows:
            process_tree = (Node(Operator.Multi))
            process_tree.add_child(single_activity)
            return process_tree
        if single_activity_pair not in log_concurrency_pairs and single_activity_pair in log_directly_follows:
            process_tree = Node(Operator.Loop)
            process_tree.add_child(single_activity)
            process_tree.add_child(Node("tau"))
            return process_tree
        else:
            process_tree = Node(Operator.Loop)
            process_tree.add_child(Node(Operator.Multi).add_child(single_activity))
            process_tree.add_child(Node("tau"))
            return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Checked for base cases")
##### OPERATORS Exclusive, Sequence, Arbitrary Order, Interleaving, Concurrent, Parallel, Loop
# split the log with an exclusive choice operator
    exclusive_choice_partitions = create_exclusive_choice_partitions(log)
    if len(exclusive_choice_partitions) > 1:
        process_tree = Node(Operator.Exclusive)
        for partition in exclusive_choice_partitions:
            process_tree.add_child(concurrency_miner(partition))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Finished Exclusive Choice partitioning")
# split the log with a sequence operator
    sequence_partitions = create_sequence_partitions(log_activities, log_concurrency_pairs, log_eventually_follows)
    if len(sequence_partitions) > 1:
        process_tree = Node(Operator.Sequence)
        for sub_log in create_sublogs_sequential(log, sequence_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Finished Sequence partitioning")
# split the log with an arbitrary order operator
    arbitrary_order_partitions = create_arbitrary_order_partitions(traces, activities, start_activities, end_activities, overlapping_relations, eventually_follows_relations, directly_follows_relations)
    if len(arbitrary_order_partitions) > 1:
        process_tree = Node(Operator.Arbitrary)
        for sublog in get_arbitrary_order_sublogs(log, arbitrary_order_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree

# split the log with an interleaving operator
    interleaving_partitions = create_interleaving_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations, minimum_self_distance_relations)
    if len(interleaving_partitions) > 1:
        process_tree = Node(Operator.Interleaving)
        for sublog in get_interleaving_sublogs(log, interleaving_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree

# split the log with a concurrent operator
    concurrent_partitions = create_concurrent_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations, minimum_self_distance_relations)
    if len(concurrent_partitions) > 1:
        process_tree = Node(Operator.Concurrent)
        for sublog in get_concurrent_sublogs(log, concurrent_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree

# split the log with a parallel operator
    parallel_partitions = create_parallel_partitions(activities, eventually_follows_relations)
    if len(parallel_partitions) > 1:
        process_tree = Node(Operator.Parallel)
        for sublog in get_parallel_sublogs(log, parallel_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree

# split the log with a loop operator
    loop_partitions = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)
    if len(loop_partitions) > 1:
        process_tree = Node(Operator.Loop)
        for sublog in get_loop_sublogs(log, loop_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree

##### FALL THROUGHS
# acitivity once per trace
    activities_once_per_trace_partitions = create_activity_once_per_trace_partitions(traces, activities)
    if len(activities_once_per_trace_partitions) >  1:
        print("Activities once per trace")
        process_tree = Node(Operator.Concurrent)
        for sublog in get_activity_once_per_trace_sublogs(log, activities_once_per_trace_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree

#activity concurrent
    activity_concurrent_partitions = get_concurrent_activity_partitions(log, activities)
    if len(activity_concurrent_partitions) > 1:
        print("Activity concurrent")
        process_tree = Node(Operator.Concurrent)
        for sublog in get_concurrent_activity_sublogs(log, activity_concurrent_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree
#tau-loop/strict-tau-loop
    #missing
# flower model
    print("Flower Model")
    flower_model_partitions = create_flower_model_partitions(activities)
    process_tree = Node(Operator.Concurrent)
    for sublog in get_flower_model_sublogs(log, flower_model_partitions):
        process_tree.add_child(concurrency_miner(sublog))
    return process_tree


