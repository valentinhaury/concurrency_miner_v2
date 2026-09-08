from itertools import permutations

from concurrency_miner_components.helper_functions.sublog_functions import create_new_trace_from_event_partition
from src.concurrency_miner_components.helper_functions.partition_functions import merge_partitions

def create_filtered_sublogs_arbitrary(log, partitions):
    sublogs = []
    for _ in partitions:
        sub_log = []
        sublogs.append(sub_log)

    for old_trace in log:
        old_trace_partitions = []
        for event in old_trace.get_events():
            old_trace_partitions.append([event])
        for (a, b) in old_trace.get_overlapping_events():
            merge_partitions(a, b, old_trace_partitions)

        old_strict_partial_order = old_trace.get_strict_partial_order()
        old_trace_partitions = _sort_trace_partitions(old_trace_partitions, old_strict_partial_order)

        partitions_assignments = []
        best_permutation = []

        indexed_partitions = list(enumerate(partitions))

        lowest_cost = float("inf")
        for indexed_permuted_partitions in permutations(indexed_partitions):
            permuted_partitions = []
            for (_ , partition) in indexed_permuted_partitions:
                permuted_partitions.append(partition)
            new_assignments, cost = _best_assignment(old_trace_partitions, permuted_partitions)
            if cost < lowest_cost:
                lowest_cost = cost
                partitions_assignments = new_assignments
                best_permutation = indexed_permuted_partitions

        for (permuted_partition_index, event_indices) in partitions_assignments:
            partition_index = best_permutation[permuted_partition_index][0]
            new_trace_events = set()

            for event_index in event_indices:
                for event in old_trace_partitions[event_index]:
                    if event.get_label() in partitions[partition_index]:
                        new_trace_events.add(event)

            # create new trace from old trace with the partitioned events
            new_trace = create_new_trace_from_event_partition(new_trace_events, old_trace)
            sublogs[partition_index].append(new_trace)
    return sublogs


def create_filtered_sublogs_sequential(log, partitions):
    sublogs = []
    for _ in partitions:
        sub_log = []
        sublogs.append(sub_log)

    for old_trace in log:
        old_trace_partitions = []
        for event in old_trace.get_events():
            old_trace_partitions.append([event])
        for (a, b) in old_trace.get_overlapping_events():
            merge_partitions(a, b, old_trace_partitions)

        old_strict_partial_order = old_trace.get_strict_partial_order()
        old_trace_partitions = _sort_trace_partitions(old_trace_partitions, old_strict_partial_order)

        partitions_assignments, cost = _best_assignment(old_trace_partitions, partitions)

        for (partition_index, assignment) in partitions_assignments:
            new_trace_events = set()
            for trace_partition_index in assignment:
                for event in old_trace_partitions[trace_partition_index]:
                    if event.get_label() in partitions[partition_index]:
                        new_trace_events.add(event)

            # create new trace from old trace with the partitioned events
            new_trace = create_new_trace_from_event_partition(new_trace_events, old_trace)

            # add the new trace to the correct sublog
            sublogs[partition_index].append(new_trace)

    return sublogs

def _sort_trace_partitions(old_trace_partitions, old_strict_partial_order):
    # sort partitions
    n = len(old_trace_partitions)
    changed = True
    while changed:
        changed = False
        for i in range(n):
            a = next(iter(old_trace_partitions[i]))
            for j in range(i + 1, n):
                b = next(iter(old_trace_partitions[j]))
                if (b, a) in old_strict_partial_order:
                    old_trace_partitions[i], old_trace_partitions[j] = (old_trace_partitions[j],
                                                                        old_trace_partitions[i])
                    changed = True
    return old_trace_partitions

def _best_assignment(event_partitions, activity_partitions):

    # cost of an event_partition if assigned to a specific activity_partition
    def _cost(event_partition, activity_partition):
        return sum(event.get_label() not in activity_partition for event in event_partition)

    possible_assignments = _possible_assignments(0, len(activity_partitions)-1, 0, len(event_partitions)-1)

    # calculate the cost for every possible assignment
    cost_list = []
    for assignment in possible_assignments:
        cost = 0
        for (activity_partition_index, event_partition_indices) in assignment:
            for event_partition_index in event_partition_indices:
                cost += _cost(event_partitions[event_partition_index], activity_partitions[activity_partition_index])
        cost_list.append(cost)

    index_of_lowest_cost = cost_list.index(min(cost_list))
    assignment_with_lowest_cost = possible_assignments[index_of_lowest_cost]
    lowest_cost = cost_list[index_of_lowest_cost]

    return assignment_with_lowest_cost, lowest_cost


def _possible_assignments(l, m, k, n):
    possible_assignments = []
    if l == m:  # end recursion when only one activity-partition is left -> assign all leftover element-partitions to that activity-partition
        assigned_elements = []
        for i in range(k, n + 1):
            assigned_elements.append(i)
        possible_assignments.insert(0, [(l, assigned_elements)])
    else:
        for j in range(n, k - 2, -1):
            assigned_elements = []
            # for the last run add the option where activity-partition m gets no event-partitions
            if j < k:
                for assignment_list in _possible_assignments(l + 1, m, k, n):
                    assignment_list.insert(0, (l, assigned_elements))
                    possible_assignments.append(assignment_list)
            # join the possible assignments to activity-partition m with the possible assignments for the rest of the activity-partitions recursively
            else:
                for i in range(k, j + 1):
                    assigned_elements.append(i)
                for assignment_list in _possible_assignments(l + 1, m, j + 1, n):
                    assignment_list.insert(0, (l, assigned_elements))
                    possible_assignments.append(assignment_list)

    return possible_assignments
