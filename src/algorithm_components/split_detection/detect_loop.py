from itertools import product, combinations

from src.data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from src.data_structures.relations.strict_partial_order import StrictPartialOrder
from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.data_structures.log import Log
from src.data_structures.trace import Trace
from src.data_structures.relations.transitive_reduced_strict_partial_order import TransitiveReducedStrictPartialOrder
from src.algorithm_components.helper_functions.partition_functions import merge_partitions


def detect_loop(log):
    return len(create_loop_partitions(log)) > 1

def get_loop_sublogs(log, loop_partitions):
    sublogs = []
    # for every partition create a new sub-log
    for partition in loop_partitions:
        new_sublog = Log([])
        # for every trace create 1-n traces in every sub-log
        # for example for trace (a b a b a)
        # if partition is {a} create traces (a) (a) (a)
        # if partition is {b} create traces (b) (b)
        for trace in log.get_traces():

            # get events and relations from trace
            transitive_reduced_strict_partial_order = trace.get_transitive_reduced_strict_partial_order()
            trace_strict_partial_order = trace.get_trace_strict_partial_order()
            partition_events = set()
            for event in trace.get_events():
                if event.get_activitiy() in partition:
                    partition_events.add(event)

            # as long as there are events from the trace left new traces are created
            while partition_events:
                # initiate new trace events
                new_trace_events = set()
                new_trace_events.add(partition_events.pop())

                # update the new_trace_events until all direct connected or overlapping events from this partition are added
                changed = True
                while changed and partition_events:
                    changed = False
                    for e_t, e_p in product(new_trace_events, partition_events):
                        # if an event is direct connected to the new trace in the old trace add it to the new trace
                        if TransitiveReducedStrictPartialOrder(e_t, e_p) in transitive_reduced_strict_partial_order or TransitiveReducedStrictPartialOrder(e_p, e_t) in transitive_reduced_strict_partial_order:
                            new_trace_events.add(e_p)
                            changed = True
                        # if an event is overlapping the new trace in the old trace add it to the new trace
                        elif not StrictPartialOrder(e_t, e_p) in trace_strict_partial_order and not StrictPartialOrder(e_p, e_t) in trace_strict_partial_order:
                            new_trace_events.add(e_p)
                            changed = True
                    # remove all events that are added to the new trace
                    partition_events = partition_events - new_trace_events

                # get new trace transitive_reduced_strict_partial_order
                new_trace_transitive_reduced_strict_partial_order = set()
                for relation in transitive_reduced_strict_partial_order:
                    if relation.get_first() in new_trace_events and relation.get_second() in new_trace_events:
                        new_trace_transitive_reduced_strict_partial_order.add(relation)
                # add the new trace to the sublog
                new_sublog.add_trace(Trace(new_trace_events, new_trace_transitive_reduced_strict_partial_order))
        # for every partition add the new sublog as a child
        sublogs.append(new_sublog)

    return sublogs

def _merge_loop_partitions(activity_a, activity_b, partitions):
    # merge partitions but keep p1 at index 0
    if activity_a in partitions[0] or activity_b in partitions[0]:
        merge_partitions(activity_a, activity_b, partitions)
        partitions.insert(0, partitions.pop())
    else:
        merge_partitions(activity_a, activity_b, partitions)

def create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations):

    partitions = []

    # create partition 1 where all start and end activities are
    partition_1 = start_activities | end_activities
    partitions.append(partition_1)

    # create all other partitions from the non-start and non-end activities
    for activity in activities - partitions[0]:
        partitions.append({activity})
    # partitions 2-n should have no direct connections between them
    for a, b in combinations(activities - partitions[0], 2):
        if DirectlyFollowsRelation(a, b) in directly_follows_relations or DirectlyFollowsRelation(b, a) in directly_follows_relations:
            merge_partitions(a, b, partitions)

    # merge overlapping partitions
    for a, b in combinations(activities, 2):
        if OverlappingRelation(a, b) in overlapping_relations:
            _merge_loop_partitions(a, b, partitions)

    # merge partitions to p1 if they can be directly reached from a start-activity that is no end-activity
    for a_start in start_activities - end_activities:
        for b in activities - partitions[0]:
            if DirectlyFollowsRelation(a_start, b) in directly_follows_relations:
                _merge_loop_partitions(a_start, b, partitions)

    # merge partitions to p1 if an end-activity that is no start-activity can be directly reached from there
    for a_end in end_activities - start_activities:
        for b in activities - partitions[0]:
            if DirectlyFollowsRelation(b, a_end) in directly_follows_relations:
                _merge_loop_partitions(a_end, b, partitions)

    # merge partitions to p1 if from a partition one but not all start-activities can be reached
    # or if a partition can be reached from one but not all end-activities
    partitions_to_merge = []
    # loop over p2 - pn
    for i in range(1, len(partitions)):

        partition = partitions[i]

        reaches_start_count = 0
        reached_by_end_count = 0

        # count how many start activities are reached from partition
        for b in partition:
            for a_start in start_activities:
                if DirectlyFollowsRelation(b, a_start) in directly_follows_relations:
                    reaches_start_count += 1
                    break # important break to not count start activities double

        # count from how many end activities partition is reached
        for b in partition:
            for a_end in end_activities:
                if DirectlyFollowsRelation(a_end, b) in directly_follows_relations:
                    reached_by_end_count += 1
                    break # important break to not count end activities double

        if 0 < reaches_start_count < len(start_activities):
            partitions_to_merge.append(i)
        elif 0 < reached_by_end_count < len(end_activities):
            partitions_to_merge.append(i)

    # starts with the highest index, so that the smaller indices are not changed
    while partitions_to_merge:
        i = partitions_to_merge.pop()
        _merge_loop_partitions(partitions[0][0], partitions[i][0], partitions)

    return partitions

