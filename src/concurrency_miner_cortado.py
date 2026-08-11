import copy
from itertools import combinations

from src.algorithm_components.helper_functions.partition_functions import merge_partitions
from cortado_core.utils.cgroups_graph import ConcurrencyGroup
from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node


def concurrency_miner_cortado(log):
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
    def compute_exclusive_choice_partitions(event_log):
        _log = copy.deepcopy(event_log)
        partitions = [[_trace] for _trace in _log]
        for t1, t2 in combinations(_log, 2):
            if len(partitions) < 2:
                break
            if not t1.isdisjoint(t2):
                p1 = []
                p2 = []
                for p in partitions:
                    if t1 in p:
                        p1 = p
                    if t2 in p:
                        p2 = p
                if p1 != p2:
                    partitions.remove(p1)
                    partitions.remove(p2)
                    p1.extend(p2)
                    partitions.append(p1)
        return partitions

    exclusive_choice_partitions = compute_exclusive_choice_partitions(log)
    if len(exclusive_choice_partitions) > 1:
        process_tree = Node(Operator.Exclusive)
        for partition in exclusive_choice_partitions:
            process_tree.add_child(concurrency_miner_cortado(partition))


    def compute_sequence_partitions(activities, concurrency_pairs, follows):
        partitions = [{_activity} for _activity in log_activities]
        for a, b in combinations(activities, 2):
        # merge partitions if activities are overlapping in log
            if (a, b) in concurrency_pairs:
                merge_partitions(a, b, partitions)
        # merge partitions if activities are pairwise reachable in log
            if (a, b) in follows and (b, a) in follows:
                merge_partitions(a, b, partitions)
        # merge partitions if activities are pairwise not-reachable in log
            if (a, b) not in follows and (b, a) not in follows:
                merge_partitions(a, b, partitions)

        for partition in partitions:
            #TODO ORDER PARTITIONS HERE OR ODER SUBLOGS LATER??? -> Does sublog computation change the order?
        return partitions


    sequence_partitions = compute_sequence_partitions(log_activities, log_concurrency_pairs, log_follows)
    if len(sequence_partitions) > 1:
        process_tree = Node(Operator.Sequence)
        sublogs = compute_sequence_sublogs(sequence_partitions, log)
        for partition in sequence_partitions:
            process_tree.add_child(concurrency_miner_cortado(partition))






