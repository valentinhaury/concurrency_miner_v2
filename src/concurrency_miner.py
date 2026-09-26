from copy import copy, deepcopy
from datetime import datetime

from infrequent_concurrency_miner import infrequent_concurrency_miner
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

from src.developement_utilities.logger import get_logger

logger = get_logger(__name__)

def concurrency_miner(
        event_log: list[Trace],
        filter_threshold: float = 0,
):
    if not 0 <= filter_threshold <= 1:
        raise ValueError("filter_threshold must be between 0 and 1")

    #logger.info("---***Starting Concurrency Miner***")
    #print(f"[{datetime.now():%H:%M:%S}]---function called concurrency miner--")
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

    # create the minimum self distance relation (contains pairs of activities where the second one is a witness of the minimum self distance relationship of the first)
    log_minimum_self_distance = compute_minimum_self_distance_relations(log_activities, log)

    logger.info("----activities in the log: %s", log_activities)

##### BASE CASES
##### end recursion and add a single activity node, a self_loop node and/or a multi_instance node
    if len(log_activities) < 2:
        single_activity = (next(iter(log_activities)))
        return get_single_activity_node(single_activity, log_overlapping_relation, log_directly_follows)

##### CORE OPERATORS Exclusive, Sequence, Arbitrary Order, Interleaving, Concurrent, Parallel, Loop
##### split the log with an exclusive choice operator
    #logger.info("Starting Exclusive Choice partitioning")
    exclusive_choice_partitions = create_exclusive_choice_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(exclusive_choice_partitions) > 1:
        logger.info("Found Exclusive Choice split, Partitions: %s", exclusive_choice_partitions)
        return create_children_from_sublogs(Node(Operator.Exclusive), create_sublogs_exclusive(log, exclusive_choice_partitions), concurrency_miner, filter_threshold)

##### split the log with a sequence operator
    #logger.info("Starting Sequence partitioning")
    sequence_partitions = create_sequence_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(sequence_partitions) > 1:
        logger.info("Found Sequence split, Partitions: %s", sequence_partitions)
        return create_children_from_sublogs(Node(Operator.Sequence), create_sublogs_general(log, sequence_partitions), concurrency_miner, filter_threshold)

##### split the log with an interleaving operator
    #logger.info("Starting Interleaving partitioning")
    interleaving_partitions = create_interleaving_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_minimum_self_distance)
    if len(interleaving_partitions) > 1:
        logger.info("Found Interleaving split, Partitions: %s", interleaving_partitions)
        return create_children_from_sublogs(Node(Operator.Interleaving), create_sublogs_general(log, interleaving_partitions), concurrency_miner, filter_threshold)

##### split the log with a concurrent operator
    #logger.info("Starting Concurrent partitioning")
    concurrent_partitions = create_concurrent_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows, log_minimum_self_distance)
    if len(concurrent_partitions) > 1:
        logger.info("Found Concurrent split, Partitions: %s", concurrent_partitions)
        return create_children_from_sublogs(Node(Operator.Concurrent), create_sublogs_general(log, concurrent_partitions), concurrency_miner, filter_threshold)

##### split the log with a parallel operator
    #logger.info("Starting Parallel partitioning")
    parallel_partitions = create_parallel_partitions(log_activities, log_overlapping_relation, log_eventually_follows)
    if len(parallel_partitions) > 1:
        logger.info("Found Parallel split, Partitions: %s", parallel_partitions)
        return create_children_from_sublogs(Node(Operator.Parallel), create_sublogs_general(log, parallel_partitions), concurrency_miner, filter_threshold)

##### split the log with a loop operator
    #logger.info("Starting Loop partitioning")
    loop_partitions = create_loop_partitions(log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_directly_follows)
    if len(loop_partitions) > 1:
        logger.info("Found Loop split, Partitions: %s", loop_partitions)
        return create_children_from_sublogs(Node(Operator.Loop), create_sublogs_loop(log, loop_partitions), concurrency_miner, filter_threshold)

##### split the log with an arbitrary order operator
    arbitrary_order_partitions = create_arbitrary_order_partitions(log, log_activities, log_start_activities, log_end_activities, log_overlapping_relation, log_follows, log_directly_follows, log_minimum_self_distance)
    if len(arbitrary_order_partitions) > 1:
        logger.info("Found Arbitrary split, Partitions: %s", arbitrary_order_partitions)
        return create_children_from_sublogs(Node(Operator.Arbitrary), create_sublogs_general(log, arbitrary_order_partitions), concurrency_miner, filter_threshold)

##### INFREQUENT
    if filter_threshold > 0:
        infrequent_result = infrequent_concurrency_miner(event_log, concurrency_miner, filter_threshold)
        if infrequent_result:
            return infrequent_result

##### FALL THROUGH
    logger.info("***Starting Fall Through***")
    print(f"[{datetime.now():%H:%M:%S}]Starting Fall Through")
##### activity once per trace
    activities_once_per_trace_partitions = create_activity_once_per_trace_partitions(log, log_activities)
    if len(activities_once_per_trace_partitions) >  1:
        logger.info("Found activities_once_per_trace split, Partitions: %s", activities_once_per_trace_partitions)
        activity = next(iter(activities_once_per_trace_partitions[0]))
        sublogs = create_sublogs_general(log, activities_once_per_trace_partitions)

        operator = Operator.Interleaving
        if _is_overlapping_somewhere(activity, log_overlapping_relation):
            operator = Operator.Concurrent

        return create_children_from_sublogs(Node(operator), sublogs, concurrency_miner, filter_threshold)

##### activity concurrent
    activity_concurrent_partitions = get_concurrent_activity_partitions(log, log_activities)
    if len(activity_concurrent_partitions) > 1:
        logger.info("Found activity_concurrent split, Partitions: %s", activity_concurrent_partitions)

        activity = next(iter(activity_concurrent_partitions[0]))
        sublogs = create_sublogs_general(log, activity_concurrent_partitions)

        operator = Operator.Interleaving
        if _is_overlapping_somewhere(activity, log_overlapping_relation):
            operator = Operator.Concurrent

        return create_children_from_sublogs(Node(operator), sublogs, concurrency_miner, filter_threshold)

##### flower model
    logger.info("Starting flower model partitioning")
    print(f"[{datetime.now():%H:%M:%S}] Starting flower model partitioning")
    flower_model_partitions = create_flower_model_partitions(log_activities)
    return create_children_from_sublogs(Node(Operator.Concurrent), create_sublogs_general(log, flower_model_partitions), concurrency_miner, filter_threshold)

def _is_overlapping_somewhere(activitiy, overlapping_relations):
    for (a, b) in overlapping_relations:
        if a != b and (a == activitiy or b == activitiy):
            return True
    return False