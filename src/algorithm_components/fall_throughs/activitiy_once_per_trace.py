import copy
from itertools import combinations

from data_structures.log import Log
from data_structures.relations.strict_partial_order import StrictPartialOrder
from data_structures.relations.transitive_reduced_strict_partial_order import TransitiveReducedStrictPartialOrder
from data_structures.trace import Trace

def create_activity_once_per_trace_partitions(traces, activities):
    activities_in_every_trace = set()
    activities_in_every_trace |= traces[0].get_activities()
    for trace in traces:
        activities_in_every_trace &= trace.get_activities()

    if activities_in_every_trace:
        partition1 = set(next(iter(activities_in_every_trace)))
        partition2 = set(activities - partition1)
        return [partition1, partition2]
    else:
        return [activities]


def get_activities_once_per_trace(traces):
    activities_in_every_trace = set()
    activities_in_every_trace |= traces[0].get_activities()
    for trace in traces:
        activities_in_every_trace &= trace.get_activities()

    return activities_in_every_trace

def create_activity_oncer_per_trace_sublogs(event_log, activity):
    # create one sublog for the extracted activity and one for the rest

    sublog_a = Log()
    sublog_b = Log()
    for trace in event_log.get_traces():

        new_trace_a_events = set()
        new_trace_a_strict_partial_order = set()
        new_trace_a_transitive_reduced_strict_partial_order = set()
        new_trace_b_events = set()
        new_trace_b_strict_partial_order = set()
        new_trace_b_transitive_reduced_strict_partial_order = set()

        # add events to the corresponding sublogs
        for event in trace.get_events():
            if event.get_activity() == activity:
                new_trace_a_events.add(event)
            else:
                new_trace_b_events.add(event)

        # initializing the strict partial orders
        for relation in trace.get_strict_partial_order():
            if relation.get_first() in new_trace_a_events and relation.get_second() in new_trace_a_events:
                new_trace_a_strict_partial_order.add(relation)
            elif relation.get_first() in new_trace_b_events and relation.get_second() in new_trace_b_events:
                new_trace_b_strict_partial_order.add(relation)

        # transitive reduction of the strict partial orders
        reduction_a = set(new_trace_a_strict_partial_order)
        reduction_b = set(new_trace_b_strict_partial_order)
        for r in new_trace_a_strict_partial_order:
            for e in new_trace_a_events:
                if StrictPartialOrder(r.get_first(), e) in new_trace_a_strict_partial_order and StrictPartialOrder(e, r.get_second()) in new_trace_a_strict_partial_order:
                    reduction_a.discard(r)
        for r in new_trace_b_strict_partial_order:
            for e in new_trace_b_events:
                if StrictPartialOrder(r.get_first(), e) in new_trace_b_strict_partial_order and StrictPartialOrder(e, r.get_second()) in new_trace_b_strict_partial_order:
                    reduction_b.discard(r)

        # adding transitive reduced strict partial orders
        for r in reduction_a:
            new_trace_a_transitive_reduced_strict_partial_order.add(TransitiveReducedStrictPartialOrder(r.get_first(), r.get_second()))

        for r in reduction_b:
            new_trace_b_transitive_reduced_strict_partial_order.add(TransitiveReducedStrictPartialOrder(r.get_first(), r.get_second()))

        # adding Traces
        sublog_a.add_trace(Trace(new_trace_a_events, new_trace_a_transitive_reduced_strict_partial_order))
        sublog_b.add_trace(Trace(new_trace_b_events, new_trace_b_transitive_reduced_strict_partial_order))

    return [sublog_b, sublog_a]