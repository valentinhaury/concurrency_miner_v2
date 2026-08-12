import copy
from itertools import combinations, permutations

from src.concurrency_miner_cortado.core_miner.exclusive_choice_partitioning import compute_exclusive_choice_partitions
from src.concurrency_miner_cortado.core_miner.sequence_partitioning import compute_sequence_partitions
from src.concurrency_miner_cortado.helper_functions.compute_sublogs import compute_sequence_sublogs
from cortado_core.utils.cgroups_graph import ConcurrencyGroup
from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node



def concurrency_miner_cortado(log):
    """
    Creates a process tree with partial order semantics.

    Args:
        event log (list[ConcurrencyGroup()]): List of ConcurrencyGroup(). Each ConcurrencyGroup represents one trace

    Returns:
        process_tree (Node): Process tree with partial order semantics.
    """
# handle empty log
    if len(log) == 0:
        return Node("tau")

# handle empty traces
    def get_tau_trace():
        tau_trace = ConcurrencyGroup()
        tau_trace.events = {"tau"}
        tau_trace.follows = set()
        tau_trace.concurrency_pairs = set()
        tau_trace.directly_follows = set()
        tau_trace.start_activities = {"tau"}
        tau_trace.end_activities = {"tau"}
        return tau_trace

    log = [get_tau_trace() if len(old_trace.events) == 0 else old_trace for old_trace in log]

# initiate log parameters
    log_activities = set()
    log_start_activities = set()
    log_end_activities = set()
    log_concurrency_pairs = set()
    log_follows = set()
    log_directly_follows = set()

    for trace in log:
        log_activities |= trace.events
        log_start_activities |= trace.start_activities
        log_end_activities |= trace.end_activities
        log_concurrency_pairs |= trace.concurrency_pairs
        log_follows |= trace.follows
        log_directly_follows |= trace.directly_follows

    # create the transitive closure of the directly follows relation of the log (different from the union of the follows)
    log_follows_closure = copy.copy(log_directly_follows)
    for r1, r2 in permutations(log_directly_follows, 2):
        if r1[1] == r2[0]:
            log_follows_closure.add((r1[0], r2[1]))

# handle single activities
    if len(log_activities) < 2:
        single_activity = (next(iter(log_activities)),next(iter(log_activities)))
        if not log_concurrency_pairs and not log_follows:
            process_tree = Node(single_activity)
            return process_tree
        single_activity_pair = (single_activity, single_activity)
        if single_activity_pair in log_concurrency_pairs and single_activity_pair in log_follows:
            process_tree = Node(Operator.Loop)
            process_tree.add_child(Node(Operator.Multi).add_child(single_activity))
            process_tree.add_child(Node("tau"))
            return process_tree
        if single_activity_pair in log_concurrency_pairs:
            process_tree = (Node(Operator.Multi))
            process_tree.add_child(single_activity)
            return process_tree
        else:
            process_tree = Node(Operator.Loop)
            process_tree.add_child(single_activity)
            process_tree.add_child(Node("tau"))
            return process_tree

##### OPERATORS Exclusive, Sequence, Arbitrary Order, Interleaving, Concurrent, Parallel, Loop

    exclusive_choice_partitions = compute_exclusive_choice_partitions(log)
    if len(exclusive_choice_partitions) > 1:
        process_tree = Node(Operator.Exclusive)
        for partition in exclusive_choice_partitions:
            process_tree.add_child(concurrency_miner_cortado(partition))

    sequence_partitions = compute_sequence_partitions(log_activities, log_concurrency_pairs, log_follows_closure)
    if len(sequence_partitions) > 1:
        process_tree = Node(Operator.Sequence)
        sublogs = compute_sequence_sublogs(sequence_partitions, log)
        for partition in sequence_partitions:
            process_tree.add_child(concurrency_miner_cortado(partition))

    arbitrary_order_partitions = compute_arbitrary_order_partitions(log, log_activities,
                                                                    log_start_activities, log_end_activities,
                                                                    log_concurrency_pairs, log_follows, log_directly_follows)






