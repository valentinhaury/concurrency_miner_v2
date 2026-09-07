from datetime import datetime

from src.concurrency_miner_components.helper_functions.compute_transitive_closure import compute_transitive_closure
from src.concurrency_miner_components.single_activity_base_case import get_single_activity_node
from src.data_structures.event import Event
from src.data_structures.trace import Trace
from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node
from src.concurrency_miner_components.helper_functions.sublog_functions import create_sublogs_loop, create_sublogs_general, create_sublogs_exclusive, create_children_from_sublogs
from src.concurrency_miner_components.helper_functions.compute_minimum_self_distance_relation import compute_minimum_self_distance_relations
from src.concurrency_miner_components.partitioning.parallel_partitioning import create_parallel_partitions
from src.concurrency_miner_components.partitioning.concurrent_partitioning import create_concurrent_partitions
from src.concurrency_miner_components.partitioning.interleaving_partitioning import create_interleaving_partitions
from src.concurrency_miner_components.partitioning.exclusive_choice_partitioning import create_exclusive_choice_partitions
from src.concurrency_miner_components.partitioning.sequence_partitioning import create_sequence_partitions
from src.concurrency_miner_components.partitioning.loop_partitioning import create_loop_partitions
from src.concurrency_miner_components.partitioning.arbitrary_order_partitioning import create_arbitrary_order_partitions
from src.concurrency_miner_components.partitioning.fall_through_partitioning import create_activity_once_per_trace_partitions, get_concurrent_activity_partitions, create_flower_model_partitions

def concurrency_miner(
        event_log: list[Trace]
):
    print("-----------------------------------------------------------------------------------------------------------")
##### handle empty log
    if not event_log:
        return Node("tau")

##### handle empty traces
    log = [Trace({Event("tau")}, set(), set(), set()) if len(old_trace.get_events()) == 0 else old_trace for old_trace in event_log]

##### initiate log parameters
    log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_follows = set(), set(), set(), set(), set(), set()

    for trace in log:
        log_activities |= trace.get_activities()                        # contains all activities, activities are always represented by their name-string
        log_start_activities |= trace.get_start_activities()            # contains all start activities
        log_end_activities |= trace.get_end_activities()                # contains all end activities
        log_overlapping_relation |= trace.get_overlapping_activities()  # contains pairs of activities that occur parallel at least once in the log
        log_directly_follows |= trace.get_directly_follows()            # contains pairs of activities where the second follows directly after the first in at least one trace
        log_follows |= trace.get_eventually_follows()                   # contains all pairs of activities where the second follows eventually after the first in at least one trace

    # create the transitive closure of the directly follows relation of the log
    log_eventually_follows = compute_transitive_closure(log_directly_follows)

    # create the transitive closure of the directly follows relation of the log (contains pairs of activities where the second one is a witness of the minimum self distance relationship of the first)
    log_minimum_self_distance = compute_minimum_self_distance_relations(log_activities, log)

##### BASE CASES
##### end recursion and add a single activity node, a self_loop node and/or a multi_instance node
    if len(log_activities) < 2:
        single_activity = (next(iter(log_activities)))
        return get_single_activity_node(single_activity, log_overlapping_relation, log_directly_follows)

##### CORE OPERATORS Exclusive, Sequence, Arbitrary Order, Interleaving, Concurrent, Parallel, Loop
##### split the log with an exclusive choice operator
    print(f"[{datetime.now():%H:%M:%S}] Starting Exclusive Choice partitioning")
    exclusive_choice_partitions = create_exclusive_choice_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(exclusive_choice_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Exclusive), create_sublogs_exclusive(log, exclusive_choice_partitions), concurrency_miner)

##### split the log with a sequence operator
    print(f"[{datetime.now():%H:%M:%S}] Starting Sequence partitioning")
    sequence_partitions = create_sequence_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(sequence_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Sequence), create_sublogs_general(log, sequence_partitions), concurrency_miner)

##### split the log with an interleaving operator
    print(f"[{datetime.now():%H:%M:%S}] Starting Interleaving partitioning")
    interleaving_partitions = create_interleaving_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_minimum_self_distance)
    if len(interleaving_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Interleaving), create_sublogs_general(log, interleaving_partitions), concurrency_miner)

##### split the log with a concurrent operator
    print(f"[{datetime.now():%H:%M:%S}] Starting Concurrent partitioning")
    concurrent_partitions = create_concurrent_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_minimum_self_distance)
    if len(concurrent_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Concurrent), create_sublogs_general(log, concurrent_partitions), concurrency_miner)

##### split the log with a parallel operator
    print(f"[{datetime.now():%H:%M:%S}] Starting Parallel partitioning")
    parallel_partitions = create_parallel_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(parallel_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Parallel), create_sublogs_general(log, parallel_partitions), concurrency_miner)

##### split the log with a loop operator
    print(f"[{datetime.now():%H:%M:%S}] Starting Loop partitioning")
    loop_partitions = create_loop_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows)
    if len(loop_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Loop), create_sublogs_loop(log, loop_partitions), concurrency_miner)

##### split the log with an arbitrary order operator
    print(f"[{datetime.now():%H:%M:%S}] Starting Arbitrary Order partitioning")
    arbitrary_order_partitions = create_arbitrary_order_partitions(log, log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_follows, log_directly_follows, log_minimum_self_distance)
    if len(arbitrary_order_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Arbitrary), create_sublogs_general(log, arbitrary_order_partitions), concurrency_miner)

##### FALL THROUGHS
##### acitivity once per trace
    print(f"[{datetime.now():%H:%M:%S}] Starting activities_once_per_trace partitioning")
    activities_once_per_trace_partitions = create_activity_once_per_trace_partitions(log, log_activities)
    if len(activities_once_per_trace_partitions) >  1:
        return create_children_from_sublogs(Node(Operator.Concurrent), create_sublogs_general(log, activities_once_per_trace_partitions), concurrency_miner)

##### activity concurrent
    print(f"[{datetime.now():%H:%M:%S}] Starting activity_concurrent partitioning")
    activity_concurrent_partitions = get_concurrent_activity_partitions(log, log_activities)
    if len(activity_concurrent_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Concurrent), create_sublogs_general(log, activity_concurrent_partitions), concurrency_miner)

##### flower model
    print(f"[{datetime.now():%H:%M:%S}] Starting flower model partitioning")
    flower_model_partitions = create_flower_model_partitions(log_activities)
    return create_children_from_sublogs(Node(Operator.Concurrent), create_sublogs_general(log, flower_model_partitions), concurrency_miner)