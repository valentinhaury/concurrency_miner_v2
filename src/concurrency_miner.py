from algorithm_components.fall_throughs.concurrent_activity import get_concurrent_activity_partitions, \
    get_concurrent_activity_sublogs
from algorithm_components.split_detection.detect_loop import create_loop_partitions
from algorithm_components.fall_throughs.activitiy_once_per_trace import create_activity_once_per_trace_partitions, \
    get_activity_once_per_trace_sublogs
from src.algorithm_components.base_cases.handle_empty_traces import handle_empty_traces
from src.data_structures.activity import Activity
from src.algorithm_components.base_cases.detect_single_activity import detect_single_activity, detect_single_loop, \
    detect_multi_instance, create_single_loop_sublog
from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node
from src.algorithm_components.split_detection.detect_arbitrary_order import get_arbitrary_order_sublogs, create_arbitrary_order_partitions
from algorithm_components.helper_functions.sublog_functions import get_loop_sublogs
from src.algorithm_components.split_detection.detect_parallel import get_parallel_sublogs, create_parallel_partitions
from src.algorithm_components.split_detection.detect_concurrent import get_concurrent_sublogs, create_concurrent_partitions
from src.algorithm_components.split_detection.detect_interleaving import create_interleaving_partitions, get_interleaving_sublogs
from src.algorithm_components.split_detection.detect_exclusive import get_exclusive_choice_sublogs, create_exclusive_choice_partitions
from src.algorithm_components.split_detection.detect_sequence import get_sequence_sublogs, create_sequence_partitions



def concurrency_miner(log):
# handle empty log
    if not log.get_traces():
        return Node(Activity("tau"))
# handle empty traces
    log = handle_empty_traces(log)
# prepare relations
    traces = log.get_traces()
    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    eventually_follows_relations = log.get_eventually_follows_relations()
    directly_follows_relations = log.get_directly_follows_relations()
    minimum_self_distance_relations = log.get_minimum_self_distance_relations()

##### BASE CASES
# end recursion and add single activity node or multi_instance_node
    if len(activities) < 2:
        if detect_single_activity(traces):
            process_tree = Node(next(iter(activities)))
            return process_tree
        if detect_multi_instance(traces):
            process_tree = Node(Operator.Multi)
            process_tree.add_child(Node(next(iter(activities))))
            return process_tree
        if detect_single_loop(traces):
            process_tree = Node(Operator.Loop)
            for sublog in create_single_loop_sublog(log):
                process_tree.add_child(concurrency_miner(sublog))
            return process_tree


##### OPERATORS Exclusive, Sequence, Arbitrary Order, Interleaving, Concurrent, Parallel, Loop
# split the log with an exclusive choice operator

    exclusive_choice_partitions = create_exclusive_choice_partitions(log)
    if len(exclusive_choice_partitions) > 1:
        process_tree = Node(Operator.Exclusive)
        for sublog in get_exclusive_choice_sublogs(exclusive_choice_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree
# split the log with a sequence operator
    sequence_partitions = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)
    if len(sequence_partitions) > 1:
        process_tree = Node(Operator.Sequence)
        for sublog in get_sequence_sublogs(log, sequence_partitions, eventually_follows_relations):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree
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
    print("1")
##### FALL THROUGHS
# acitivity once per trace
    activities_once_per_trace_partitions = create_activity_once_per_trace_partitions(traces, activities)
    if len(activities_once_per_trace_partitions) >  1:
        process_tree = Node(Operator.Concurrent)
        for sublog in get_activity_once_per_trace_sublogs(log, activities_once_per_trace_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree

    print("2")
#activity concurrent
    activity_concurrent_partitions = get_concurrent_activity_partitions(log, activities)
    if len(activity_concurrent_partitions) > 1:
        process_tree = Node(Operator.Concurrent)
        for sublog in get_concurrent_activity_sublogs(log, activity_concurrent_partitions):
            process_tree.add_child(concurrency_miner(sublog))
        return process_tree
#tau-loop/strict-tau-loop
    #missing
# flower model

