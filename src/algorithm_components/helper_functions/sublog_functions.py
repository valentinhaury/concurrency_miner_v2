from itertools import product

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
                if event.get_label() in partition:
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
        for old_trace in log:

            new_trace_events = partition & old_trace.get_events()

            new_trace_transitive_reduced_strict_partial_order = {
                relation
                for relation in old_trace.get_transitive_reduced_strict_partial_order()
                if set(relation).issubset(new_trace_events)
            }
            new_trace_strict_partial_order = {
                relation
                for relation in old_trace.get_strict_partial_order()
                if set(relation).issubset(new_trace_events)
            }

            new_trace_overlapping_relations = {
                relation
                for relation in old_trace.get_overlapping_relations()
                if set(relation).issubset(new_trace_events)
            }

            sub_log.append(
                Trace(
                    new_trace_events,
                    new_trace_transitive_reduced_strict_partial_order,
                    new_trace_strict_partial_order,
                    new_trace_overlapping_relations)
            )
        sublogs.append(sub_log)
    return sublogs

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
            trace_strict_partial_order = trace.get_strict_partial_order()
            partition_events = set()
            for event in trace.get_events():
                if event.get_label() in partition:
                    partition_events.add(event)

            # if the activities from this partition are not in the trace, add an empty trace
            if not partition_events:
                new_sublog.add_trace(Trace(set(), set()))

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
