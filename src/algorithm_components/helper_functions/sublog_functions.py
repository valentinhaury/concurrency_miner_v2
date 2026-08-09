from itertools import permutations

from src.data_structures.relations.strict_partial_order import StrictPartialOrder
from src.data_structures.relations.transitive_reduced_strict_partial_order import TransitiveReducedStrictPartialOrder
from src.data_structures.log import Log
from src.data_structures.trace import Trace

def create_sublogs_concurrent(log, partitions):
    sublogs = []
    for partition in partitions:
        sub_log = []
        for trace in log.get_traces():

            new_trace_events = set()
            new_trace_strict_partial_order = set()
            new_trace_transitive_reduced_strict_partial_order = set()

            # add events to the trace
            for event in trace.get_events():
                if event.get_activity() in partition:
                    new_trace_events.add(event)

            # initializing the strict partial order
            for relation in trace.get_strict_partial_order():
                if relation.get_first() in new_trace_events and relation.get_second() in new_trace_events:
                    new_trace_strict_partial_order.add(relation)

            # transitive reduction of the strict partial order
            reduction = set(new_trace_strict_partial_order)
            for r in new_trace_strict_partial_order:
                for e in new_trace_events:
                    if StrictPartialOrder(r.get_first(), e) in new_trace_strict_partial_order and StrictPartialOrder(e, r.get_second()) in new_trace_strict_partial_order:
                        reduction.discard(r)

            # adding transitive reduced strict partial orders
            for r in reduction:
                new_trace_transitive_reduced_strict_partial_order.add(TransitiveReducedStrictPartialOrder(r.get_first(), r.get_second()))

            sub_log.append(Trace(new_trace_events, new_trace_transitive_reduced_strict_partial_order))
        sublogs.append(Log(sub_log))

    return sublogs

def create_sublogs_sequential(log, partitions):
    sublogs = []
    for partition in partitions:
        sub_log = []
        for trace in log.get_traces():

            new_trace_events = set()
            new_trace_transitive_reduced_strict_partial_order = set()

            # add events to new trace
            for event in trace.get_events():
                if event.get_activity() in partition:
                    new_trace_events.add(event)

            # add relations to new event
            for relation in trace.get_transitive_reduced_strict_partial_order():
                if relation.get_first() in new_trace_events and relation.get_second() in new_trace_events:
                    new_trace_transitive_reduced_strict_partial_order.add(relation)

            sub_log.append(Trace(new_trace_events, new_trace_transitive_reduced_strict_partial_order))
        sublogs.append(Log(sub_log))

    return sublogs
