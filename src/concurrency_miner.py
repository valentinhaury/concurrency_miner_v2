from src.algorithm_components.fall_throughs.flower_model import get_loop_activities
from algorithm_components.helper_functions import minimum_self_distance_relation
from src.algorithm_components.helper_functions.sublog_functions import get_log_without_activity
from src.algorithm_components.fall_throughs.activitiy_once_per_trace import detect_activity_once_per_trace, \
    get_activities_once_per_trace
from src.algorithm_components.base_cases.handle_empty_traces import handle_empty_traces
from src.data_structures.activity import Activity
from src.algorithm_components.base_cases.detect_single_activity import detect_single_activity, get_single_activity
from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node
from src.algorithm_components.split_detection.detect_arbitrary_order import detect_arbitrary_order, \
    get_arbitrary_order_sublogs, create_arbitrary_order_partitions
from src.algorithm_components.split_detection.detect_loop import detect_loop, get_loop_sublogs
from src.algorithm_components.split_detection.detect_parallel import detect_parallel, get_parallel_sublogs
from src.algorithm_components.split_detection.detect_concurrent import detect_concurrent, get_concurrent_sublogs
from src.algorithm_components.split_detection.detect_interleafing import create_interleaving_partitions, get_interleaving_sublogs
from src.algorithm_components.split_detection.detect_exclusive import detect_exclusive, get_exclusive_choice_sublogs
from src.algorithm_components.split_detection.detect_sequence import get_sequence_sublogs, \
    create_sequence_partitions
from src.algorithm_components.split_detection.detect_multi_instance import get_multi_instance_activities

def concurrency_miner(log, multi_instance_activities=None):
    if not log.get_traces():
        return Node(Activity("tau"))

# prepare relations
    traces = log.get_traces()
    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    eventually_follows_relations = log.get_eventually_follows_relations()
    directly_follows_relations = log.get_directly_follows_relations()
    minimum_self_distance_relations = log.get_minimum_self_distance_relations()

# check for multi_instance activities
    if not multi_instance_activities:
        multi_instance_activities = get_multi_instance_activities(log)

##### BASE CASES
# add Activity("tau") to empty traces
    handle_empty_traces(log)
# end recursion and add single activity node
    if detect_single_activity(log):
        activity = get_single_activity(log)
        if activity.activity_exists_by_label(multi_instance_activities):
            process_tree = Node(Operator.Multi)
            process_tree.add_child(Node(activity))
        else:
            process_tree = Node(activity)
        return process_tree

##### OPERATORS Exclusive, Sequence, Arbitrary Order, Interleaving, Concurrent, Parallel, Loop
# split the log with an exclusive choice operator
    if detect_exclusive(log):
        process_tree = Node(Operator.Exclusive)
        for sublog in get_exclusive_choice_sublogs(log):
            process_tree.add_child(concurrency_miner(sublog, multi_instance_activities))
        return process_tree
# split the log with a sequence operator
    sequence_partitions = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)
    if len(sequence_partitions) > 1:
        process_tree = Node(Operator.Sequence)
        for sublog in get_sequence_sublogs(log, sequence_partitions, eventually_follows_relations):
            process_tree.add_child(concurrency_miner(sublog, multi_instance_activities))
        return process_tree
# split the log with an arbitrary order operator
    arbitrary_order_partitions = create_arbitrary_order_partitions(traces, activities, overlapping_relations, eventually_follows_relations)
    if len(arbitrary_order_partitions) > 1:
        process_tree = Node(Operator.Arbitrary)
        for sublog in get_arbitrary_order_sublogs(log, arbitrary_order_partitions):
            process_tree.add_child(concurrency_miner(sublog, multi_instance_activities))
        return process_tree
# split the log with an interleaving operator
    interleaving_partitions = create_interleaving_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations, minimum_self_distance_relations)
    if len(interleaving_partitions) > 1:
        process_tree = Node(Operator.Interleaving)
        for sublog in get_interleaving_sublogs(log, interleaving_partitions):
            process_tree.add_child(concurrency_miner(sublog, multi_instance_activities))
        return process_tree

# split the log with a concurrent operator
    elif detect_concurrent(log):
        process_tree = Node(Operator.Concurrent)
        for sublog in get_concurrent_sublogs(log):
            process_tree.add_child(concurrency_miner(sublog, multi_instance_activities))
        return process_tree
# split the log with a parallel operator
    elif detect_parallel(log):
        process_tree = Node(Operator.Parallel)
        for sublog in get_parallel_sublogs(log):
            process_tree.add_child(concurrency_miner(sublog, multi_instance_activities))
        return process_tree
# split the log with a loop operator
    elif detect_loop(log):
        process_tree = Node(Operator.Loop)
        for sublog in get_loop_sublogs(log):
            process_tree.add_child(concurrency_miner(sublog, multi_instance_activities))
        return process_tree

##### FALL THROUGH

# acitivity once per trace
    elif detect_activity_once_per_trace(log):
        process_tree = Node(Operator.Concurrent)
        activity = get_activities_once_per_trace(log)[0]
        process_tree.add_child(activity)
        new_log = get_log_without_activity(log, activity)
        process_tree.add_child(concurrency_miner(new_log, multi_instance_activities))
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
