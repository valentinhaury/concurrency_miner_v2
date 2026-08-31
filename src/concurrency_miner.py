import copy
from datetime import datetime
from itertools import permutations

from src.data_structures.event import Event
from src.data_structures.trace import Trace
from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node

from src.concurrency_miner_components.helper_functions.sublog_functions import create_sublogs_loop, \
    create_sublogs_general, create_sublogs_exclusive
from src.concurrency_miner_components.helper_functions.compute_minimum_self_distance_relation import \
    compute_minimum_self_distance_relations

from src.concurrency_miner_components.partitioning.parallel_partitioning import create_parallel_partitions
from src.concurrency_miner_components.partitioning.concurrent_partitioning import create_concurrent_partitions
from src.concurrency_miner_components.partitioning.interleaving_partitioning import create_interleaving_partitions
from src.concurrency_miner_components.partitioning.exclusive_choice_partitioning import create_exclusive_choice_partitions
from src.concurrency_miner_components.partitioning.sequence_partitioning import create_sequence_partitions
from src.concurrency_miner_components.partitioning.loop_partitioning import create_loop_partitions
from src.concurrency_miner_components.partitioning.arbitrary_order_partitioning import create_arbitrary_order_partitions
from src.concurrency_miner_components.partitioning.fall_through_partitioning import create_activity_once_per_trace_partitions, \
    get_concurrent_activity_partitions, create_flower_model_partitions


def concurrency_miner(
        event_log: list[Trace]
):
    print("-----------------------------------------------------------------------------------------------------------")
    print(f"[{datetime.now():%H:%M:%S}] Initiating Log")
# handle empty log
    if not event_log:
        return Node("tau")

# handle empty traces
    log = [Trace({Event("tau")}, set(), set(), set()) if len(old_trace.get_events()) == 0 else old_trace for old_trace in event_log]

# initiate log parameters
    log_activities = set()              #contains all activities, activities are always represented by their name-string
    log_start_activities = set()        #contains all start activities
    log_end_activities = set()          #contains all end activities
    log_overlapping_relation = set()    #contains pairs of activities that occur parallel at least once in the log
    log_directly_follows = set()        #contains pairs of activities where the second follows directly after the first in at least one trace
    log_eventually_follows = set()      #contains the transitive closure of the directly follows relation
    log_minimum_self_distance = set()   #contains pairs of activities where the second one is a witness of the minimum self distance relationship of the first
    log_follows = set()                 # contains all pars of activities where the second follows eventually after the first in at least one trace

    for trace in log:
        log_activities |= trace.get_activities()
        log_start_activities |= trace.get_start_activities()
        log_end_activities |= trace.get_end_activities()
        log_overlapping_relation |= trace.get_overlapping_activities()
        log_directly_follows |= trace.get_directly_follows()
        log_follows |= trace.get_eventually_follows()

    # create the transitive closure of the directly follows relation of the log
    log_eventually_follows |= copy.copy(log_directly_follows)
    changed = True
    while changed:
        changed = False
        for r1, r2 in permutations(log_eventually_follows, 2):
            if r1[1] == r2[0]:
                if (r1[0], r2[1]) not in log_eventually_follows:
                    log_eventually_follows.add((r1[0], r2[1]))
                    changed = True

    log_minimum_self_distance |= compute_minimum_self_distance_relations(log_activities, log)
    print(f"[{datetime.now():%H:%M:%S}] Checking for base cases")
##### BASE CASES
# end recursion and add a single activity node, a self_loop node and/or a multi_instance node
    if len(log_activities) < 2:
        single_activity = (next(iter(log_activities)))
        if not log_overlapping_relation and not log_directly_follows:
            process_tree = Node(single_activity)
            return process_tree
        single_activity_pair = (single_activity, single_activity)
        if single_activity_pair in log_overlapping_relation and single_activity_pair not in log_directly_follows:
            process_tree = (Node(Operator.Multi))
            process_tree.add_child(Node(single_activity))
            return process_tree
        if single_activity_pair not in log_overlapping_relation and single_activity_pair in log_directly_follows:
            process_tree = Node(Operator.Loop)
            process_tree.add_child(Node(single_activity))
            process_tree.add_child(Node("tau"))
            return process_tree
        else:
            multi_node = Node(Operator.Multi)
            multi_node.add_child(Node(single_activity))
            process_tree = Node(Operator.Loop)
            process_tree.add_child(multi_node)
            process_tree.add_child(Node("tau"))
            return process_tree


    print(f"[{datetime.now():%H:%M:%S}] Starting Exclusive Choice partitioning")
##### OPERATORS Exclusive, Sequence, Arbitrary Order, Interleaving, Concurrent, Parallel, Loop
# split the log with an exclusive choice operator
    exclusive_choice_partitions = create_exclusive_choice_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(exclusive_choice_partitions) > 1:
        process_tree = Node(Operator.Exclusive)
        for sub_log in create_sublogs_exclusive(log, exclusive_choice_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting Sequence partitioning")
# split the log with a sequence operator
    sequence_partitions = create_sequence_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(sequence_partitions) > 1:
        process_tree = Node(Operator.Sequence)
        for sub_log in create_sublogs_general(log, sequence_partitions): #create_sublogs_sequential(log, sequence_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting Interleaving partitioning")
# split the log with an interleaving operator
    interleaving_partitions = create_interleaving_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_minimum_self_distance)
    if len(interleaving_partitions) > 1:
        process_tree = Node(Operator.Interleaving)
        for sub_log in create_sublogs_general(log, interleaving_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting Concurrent partitioning")
# split the log with a concurrent operator
    concurrent_partitions = create_concurrent_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_minimum_self_distance)
    if len(concurrent_partitions) > 1:
        process_tree = Node(Operator.Concurrent)
        for sub_log in create_sublogs_general(log, concurrent_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting Parallel partitioning")
# split the log with a parallel operator
    parallel_partitions = create_parallel_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(parallel_partitions) > 1:
        process_tree = Node(Operator.Parallel)
        for sub_log in create_sublogs_general(log, parallel_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
            for trace in sub_log:
                print("t." + str(trace))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting Loop partitioning")
# split the log with a loop operator
    loop_partitions = create_loop_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows)
    if len(loop_partitions) > 1:
        process_tree = Node(Operator.Loop)
        for sub_log in create_sublogs_loop(log, loop_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting Arbitrary Order partitioning")
# split the log with an arbitrary order operator
    arbitrary_order_partitions = create_arbitrary_order_partitions(log, log_activities, log_start_activities,
                                                                   log_end_activities, log_overlapping_relation,
                                                                   log_follows, log_directly_follows, log_minimum_self_distance)
    if len(arbitrary_order_partitions) > 1:
        process_tree = Node(Operator.Arbitrary)
        for sub_log in create_sublogs_general(log, arbitrary_order_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting activities_once_per_trace partitioning")
##### FALL THROUGHS
# acitivity once per trace
    activities_once_per_trace_partitions = create_activity_once_per_trace_partitions(log, log_activities)
    if len(activities_once_per_trace_partitions) >  1:
        process_tree = Node(Operator.Concurrent)
        for sub_log in create_sublogs_general(log, activities_once_per_trace_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting activity_concurrent partitioning")
#activity concurrent
    activity_concurrent_partitions = get_concurrent_activity_partitions(log, log_activities)
    if len(activity_concurrent_partitions) > 1:
        process_tree = Node(Operator.Concurrent)
        for sub_log in create_sublogs_general(log, activity_concurrent_partitions):
            process_tree.add_child(concurrency_miner(sub_log))
        return process_tree

    print(f"[{datetime.now():%H:%M:%S}] Starting flower model partitioning")
# flower model
    flower_model_partitions = create_flower_model_partitions(log_activities)
    process_tree = Node(Operator.Concurrent)
    for sub_log in create_sublogs_general(log, flower_model_partitions):
        process_tree.add_child(concurrency_miner(sub_log))

    return process_tree


