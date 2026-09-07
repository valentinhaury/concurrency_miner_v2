from collections import Counter
from collections.abc import Callable
from datetime import datetime

from src.concurrency_miner_components.helper_functions.compute_minimum_self_distance_relation import compute_minimum_self_distance_relations
from src.concurrency_miner_components.helper_functions.compute_transitive_closure import compute_transitive_closure
from src.concurrency_miner_components.helper_functions.sublog_functions import create_children_from_sublogs, \
     create_sublogs_general, create_sublogs_loop
from src.concurrency_miner_components.partitioning.arbitrary_order_partitioning import create_arbitrary_order_partitions
from src.concurrency_miner_components.partitioning.concurrent_partitioning import create_concurrent_partitions
from src.concurrency_miner_components.partitioning.exclusive_choice_partitioning import create_exclusive_choice_partitions
from src.concurrency_miner_components.partitioning.interleaving_partitioning import create_interleaving_partitions
from src.concurrency_miner_components.partitioning.loop_partitioning import create_loop_partitions
from src.concurrency_miner_components.partitioning.parallel_partitioning import create_parallel_partitions
from src.concurrency_miner_components.partitioning.sequence_partitioning import create_sequence_partitions
from src.concurrency_miner_components.single_activity_base_case import get_single_activity_node

from src.infrequent_concurrency_miner_components.infrequent_exclusive_log_splitting import create_filtered_sublogs_exclusive

from src.data_structures.process_tree_operator import Operator
from src.data_structures.event import Event
from src.data_structures.process_tree import Node
from src.data_structures.trace import Trace

def infrequent_concurrency_miner(
        event_log: list[Trace],
        concurrency_miner: Callable[[list[Trace], int], Node],
        filter_threshold: float = 0,

):
    print("INFREQUENT-----------------------------------------------------------------------------------------------------------")

    ##### handle empty log
    if not event_log:
        return Node("tau")

##### handle empty traces
    number_of_empty_traces = 0
    for trace in event_log:
        if len(trace.get_events()) == 0:
            number_of_empty_traces += 1

    log = []
    #TODO maybe this should already be at threshold / 10 ??
    if number_of_empty_traces / len(event_log) >= filter_threshold:
        log = [Trace({Event("tau")}, set(), set(), set()) if len(old_trace.get_events()) == 0 else old_trace for old_trace in event_log]
    else:
        for trace in event_log:
            if len(trace.get_events()) > 0:
                log.append(trace)

##### initiate log parameters
    log_activities, log_start_activities, log_end_activities, log_follows = set(), set(), set(), set()
    counter_overlapping, counter_directly_follows = Counter(), Counter()

    for trace in log:
        log_activities |= trace.get_activities()                        # contains all activities, activities are always represented by their name-string
        log_start_activities |= trace.get_start_activities()            # contains all start activities
        log_end_activities |= trace.get_end_activities()                # contains all end activities
        #log_overlapping_relation |= trace.get_overlapping_activities()  # contains pairs of activities that occur parallel at least once in the log
        counter_overlapping.update(trace.get_overlapping_activities())
        #log_directly_follows |= trace.get_directly_follows()            # contains pairs of activities where the second follows directly after the first in at least one trace
        counter_directly_follows.update(trace.get_directly_follows())
        log_follows |= trace.get_eventually_follows()                   # contains all pairs of activities where the second follows eventually after the first in at least one trace

    def filter_relation(counter):
        max_counts_out = {}
        max_counts_in = {}
        for (a, b), count in counter.items():
            max_counts_out[a] = max(max_counts_out.get(a, 0), count)
            max_counts_in[b] = max(max_counts_in.get(b, 0), count)
        filtered_relation = set()
        for (a, b), count in counter.items():
            if count / max_counts_out[a] >= filter_threshold or count / max_counts_in[b] >= filter_threshold:
                filtered_relation.add((a, b))
        return filtered_relation

##### filter directly follows
    filtered_directly_follows = filter_relation(counter_directly_follows)

##### filter overlapping
    filtered_overlapping = filter_relation(counter_overlapping)


    # create the transitive closure of the directly follows relation of the log
    log_eventually_follows = compute_transitive_closure(filtered_directly_follows)

    # create the minimum self distance relation  (contains pairs of activities where the second one is a witness of the minimum self distance relationship of the first)
    log_minimum_self_distance = compute_minimum_self_distance_relations(log_activities, log)

##### BASE CASES
##### end recursion and add a single activity node, a self_loop node and/or a multi_instance node
    if len(log_activities) < 2:
        single_activity = (next(iter(log_activities)))
        return get_single_activity_node(single_activity, filtered_overlapping, filtered_directly_follows)

##### CORE OPERATORS Exclusive, Sequence, Arbitrary Order, Interleaving, Concurrent, Parallel, Loop
##### split the log with an exclusive choice operator
    print(f"[{datetime.now():%H:%M:%S}] Starting FILTERED Exclusive Choice partitioning")
    exclusive_choice_partitions = create_exclusive_choice_partitions(log_activities, filtered_overlapping, log_eventually_follows)
    if len(exclusive_choice_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Exclusive), create_filtered_sublogs_exclusive(log, exclusive_choice_partitions), concurrency_miner, filter_threshold) #TODO implement NEW sublog creation for infrequent

##### split the log with a sequence operator
    print(f"[{datetime.now():%H:%M:%S}] Starting FILTERED Sequence partitioning")
    sequence_partitions = create_sequence_partitions(log_activities, filtered_overlapping, log_eventually_follows)
    if len(sequence_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Sequence), create_sublogs_general(log, sequence_partitions), concurrency_miner, filter_threshold) #TODO implement NEW sublog creation for infrequent

##### split the log with an interleaving operator
    print(f"[{datetime.now():%H:%M:%S}] Starting FILTERED Interleaving partitioning")
    interleaving_partitions = create_interleaving_partitions(log_activities, log_start_activities, log_end_activities, filtered_overlapping, filtered_directly_follows, log_minimum_self_distance)
    if len(interleaving_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Interleaving), create_sublogs_general(log, interleaving_partitions), concurrency_miner, filter_threshold) #TODO implement NEW sublog creation for infrequent

##### split the log with a concurrent operator
    print(f"[{datetime.now():%H:%M:%S}] Starting FILTERED Concurrent partitioning")
    concurrent_partitions = create_concurrent_partitions(log_activities, log_start_activities, log_end_activities, filtered_overlapping, filtered_directly_follows, log_minimum_self_distance)
    if len(concurrent_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Concurrent), create_sublogs_general(log, concurrent_partitions), concurrency_miner, filter_threshold) #TODO implement NEW sublog creation for infrequent

##### split the log with a parallel operator
    print(f"[{datetime.now():%H:%M:%S}] Starting FILTERED Parallel partitioning")
    parallel_partitions = create_parallel_partitions(log_activities, filtered_overlapping, log_eventually_follows)
    if len(parallel_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Parallel), create_sublogs_general(log, parallel_partitions), concurrency_miner, filter_threshold) #TODO implement NEW sublog creation for infrequent

##### split the log with a loop operator
    print(f"[{datetime.now():%H:%M:%S}] Starting FILTERED Loop partitioning")
    loop_partitions = create_loop_partitions(log_activities, log_start_activities, log_end_activities, filtered_overlapping, filtered_directly_follows)
    if len(loop_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Loop), create_sublogs_loop(log, loop_partitions), concurrency_miner, filter_threshold) #TODO implement NEW sublog creation for infrequent

##### split the log with an arbitrary order operator
    print(f"[{datetime.now():%H:%M:%S}] Starting FILTERED Arbitrary Order partitioning")
    arbitrary_order_partitions = create_arbitrary_order_partitions(log, log_activities, log_start_activities, log_end_activities, filtered_overlapping, log_follows, filtered_directly_follows, log_minimum_self_distance)
    if len(arbitrary_order_partitions) > 1:
        return create_children_from_sublogs(Node(Operator.Arbitrary), create_sublogs_general(log, arbitrary_order_partitions), concurrency_miner, filter_threshold) #TODO implement NEW sublog creation for infrequent

    return False