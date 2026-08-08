from algorithm_components.split_detection.detect_loop import create_loop_partitions
from src.algorithm_components.fall_throughs.flower_model import get_loop_activities
from src.algorithm_components.helper_functions.sublog_functions import get_log_without_activity
from src.algorithm_components.fall_throughs.activitiy_once_per_trace import detect_activity_once_per_trace, get_activities_once_per_trace
from src.algorithm_components.base_cases.handle_empty_traces import handle_empty_traces
from src.data_structures.activity import Activity
from src.algorithm_components.base_cases.detect_single_activity import detect_single_activity
from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node
from src.algorithm_components.split_detection.detect_arbitrary_order import get_arbitrary_order_sublogs, create_arbitrary_order_partitions
from src.algorithm_components.split_detection.detect_loop import get_loop_sublogs
from src.algorithm_components.split_detection.detect_parallel import get_parallel_sublogs, create_parallel_partitions
from src.algorithm_components.split_detection.detect_concurrent import get_concurrent_sublogs, create_concurrent_partitions
from src.algorithm_components.split_detection.detect_interleaving import create_interleaving_partitions, get_interleaving_sublogs
from src.algorithm_components.split_detection.detect_exclusive import get_exclusive_choice_sublogs, create_exclusive_choice_partitions
from src.algorithm_components.split_detection.detect_sequence import get_sequence_sublogs, create_sequence_partitions
from src.algorithm_components.split_detection.detect_multi_instance import detect_multi_instance


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

    print("LOG: " + str(log))

##### BASE CASES
# end recursion and add single activity node or multi_instance_node
    if len(activities) < 2:
        if detect_single_activity(traces):
            process_tree = Node(next(iter(activities)))
            return process_tree
        elif detect_multi_instance(traces):
            process_tree = Node(Operator.Multi)
            process_tree.add_child(Node(activities[0]))
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
    arbitrary_order_partitions = create_arbitrary_order_partitions(traces, activities, overlapping_relations, eventually_follows_relations)
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

##### FALL THROUGH

# acitivity once per trace
    elif detect_activity_once_per_trace(log):
        process_tree = Node(Operator.Concurrent)
        activity = get_activities_once_per_trace(log)[0]
        process_tree.add_child(activity)
        new_log = get_log_without_activity(log, activity)
        process_tree.add_child(concurrency_miner(new_log))
        return process_tree
#activity concurrent
    #missing
#tau-loop/strict-tau-loop
    #missing
# flower model → aktivitäten die in einem trace mehrfach vorkommen in einen tau-loop stecken
    else:
        loop_activities = get_loop_activities(log)
        activities = get_activities_once_per_trace(log)
        optional_activities = []
        for activity in log.get_activities_by_label():
            if not (activity.activity_exists_by_label(loop_activities)
                    or activity.activity_exists_by_label(activities)):
                optional_activities.append(activity)
        process_tree = Node(Operator.Concurrent)
        for activity in activities:
            process_tree.add_child(Node(activity))
        for activity in loop_activities:
            child = Node(Operator.Loop)
            child.add_child(Node(Activity("tau")))
            child.add_child(Node(activity))
            process_tree.add_child(child)
        for activity in optional_activities:
            child = Node(Operator.Exclusive)
            child.add_child(Node(Activity("tau")))
            child.add_child(Node(activity))
            process_tree.add_child(child)
        return process_tree
