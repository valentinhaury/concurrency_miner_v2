from src.data_structures.log import Log
from src.data_structures.trace import Trace

def create_sublogs_concurrent(log, partitions):
    sublogs = []

    for partition in partitions:
        sub_log = []
        for old_trace in log.get_traces():

            # new events are old events that are present in the partition
            new_trace_events = partition & old_trace.get_events()

            # new strict partial order is old strict partial order
            new_trace_strict_partial_order = {
                relation
                for relation in old_trace.get_strict_partial_order()
                if set(relation).issubset(new_trace_events)
            }

            # new transitive reduced strict partial order is the transitive reduction of the old strict partial order
            new_trace_transitive_reduced_strict_partial_order = set(new_trace_strict_partial_order)
            for r in new_trace_strict_partial_order:
                for e in new_trace_events:
                    if (r[0], e) in new_trace_strict_partial_order and (e, r[1]) in new_trace_strict_partial_order:
                        new_trace_transitive_reduced_strict_partial_order.discard(r)

            # new overlapping relation is old overlapping relation
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
                    new_trace_overlapping_relations
                )
            )
        sublogs.append(Log(sub_log))

    return sublogs

def create_sublogs_sequential(log, partitions):
    sublogs = []
    for partition in partitions:
        sub_log = []
        for old_trace in log:

            # new events are old events that are present in the partition
            new_trace_events = partition & old_trace.get_events()

            # new transitive reduced strict partial order is old transitive reduced strict partial order
            new_trace_transitive_reduced_strict_partial_order = {
                relation
                for relation in old_trace.get_transitive_reduced_strict_partial_order()
                if set(relation).issubset(new_trace_events)
            }

            # new strict partial order is old strict partial order
            new_trace_strict_partial_order = {
                relation
                for relation in old_trace.get_strict_partial_order()
                if set(relation).issubset(new_trace_events)
            }

            # new overlapping relation is old overlapping relation
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
                    new_trace_overlapping_relations
                )
            )
        sublogs.append(sub_log)
    return sublogs

def create_sublogs_loop(log, loop_partitions):
    sublogs = []
    # for every partition create a new sub-log
    for partition in loop_partitions:
        sub_log = []
        # for every trace create 1-n traces in every sub-log
        # for example for trace (a b a b a)
        # if partition is {a} create traces (a) (a) (a)
        # if partition is {b} create traces (b) (b)
        for old_trace in log.get_traces():

            # new events are old events that are present in the partition
            partition_events = partition & old_trace.get_events()

            # if the activities from this partition are not in the trace, add an empty trace
            if not partition_events:
                sub_log.append(Trace({"tau"}, set(), set(), set()))

            # as long as there are events from the trace left new traces are created
            while partition_events:
                # initiate new trace events
                new_trace_events = set()
                new_trace_events.add(partition_events.pop())

                # update the new_trace_events until all direct connected or overlapping events from this partition are added
                changed = True
                while changed and partition_events:
                    changed = False
                    for e1, e2 in old_trace.get_transitive_reduced_strict_partial_order():
                        if e1 in new_trace_events:
                            new_trace_events.add(e2)
                            changed = True
                        if e2 in new_trace_events:
                            new_trace_events.add(e1)
                            changed = True

                    for e1, e2 in old_trace.get_overlapping_events():
                        if e1 in new_trace_events:
                            new_trace_events.add(e2)
                            changed = True

                # remove all events that are added to the new trace
                partition_events = partition_events - new_trace_events

                # new transitive reduced strict partial order is old transitive reduced strict partial order
                new_trace_transitive_reduced_strict_partial_order = {
                    relation
                    for relation in old_trace.get_transitive_reduced_strict_partial_order()
                    if set(relation).issubset(new_trace_events)
                }

                # new strict partial order is old strict partial order
                new_trace_strict_partial_order = {
                    relation
                    for relation in old_trace.get_strict_partial_order()
                    if set(relation).issubset(new_trace_events)
                }

                # new overlapping relation is old overlapping relation
                new_trace_overlapping_relations = {
                    relation
                    for relation in old_trace.get_overlapping_relations()
                    if set(relation).issubset(new_trace_events)
                }

                # add the new trace to the sublog
                sub_log.append(
                    Trace(
                        new_trace_events,
                        new_trace_transitive_reduced_strict_partial_order,
                        new_trace_strict_partial_order,
                        new_trace_overlapping_relations
                    )
                )
        # for every partition add the new sublog as a child
        sublogs.append(sub_log)

    return sublogs
