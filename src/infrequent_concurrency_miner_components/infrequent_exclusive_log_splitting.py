from data_structures.trace import Trace


def create_filtered_sublogs_exclusive(log, partitions):
    sublogs = []
    for _ in partitions:
        sub_log = []
        sublogs.append(sub_log)

    # find for every trace the partition where the least amount of events have to be removed from the trace
    for old_trace in log:
        greatest_number = 0
        greatest_number_index = 0
        for i, partition in enumerate(partitions):
            partition_number = 0
            for event in old_trace.get_events():
                if event.get_label() in partition:
                    partition_number += 1
            if partition_number > greatest_number:
                greatest_number = partition_number
                greatest_number_index = i

        # new trace events are old events in the partition
        new_trace_events = {event for event in old_trace.get_events() if event.get_label() in partitions[greatest_number_index]}

        # new strict partial order is old strict partial order
        new_trace_strict_partial_order = {
            relation
            for relation in old_trace.get_strict_partial_order()
            if set(relation).issubset(new_trace_events)
        }

        # new transitive reduced strict partial order is the transitive reduction of the new strict partial order
        new_trace_transitive_reduced_strict_partial_order = set(new_trace_strict_partial_order)
        for r in new_trace_strict_partial_order:
            for e in new_trace_events:
                if (r[0], e) in new_trace_strict_partial_order and (e, r[1]) in new_trace_strict_partial_order:
                    new_trace_transitive_reduced_strict_partial_order.discard(r)

        # new overlapping relation is old overlapping relation
        new_trace_overlapping_relations = {
            relation
            for relation in old_trace.overlapping_relations
            if set(relation).issubset(new_trace_events)
        }
        new_trace = Trace(
            new_trace_events,
            new_trace_transitive_reduced_strict_partial_order,
            new_trace_strict_partial_order,
            new_trace_overlapping_relations
        )
        sublogs[greatest_number_index].append(
            new_trace
        )

    return sublogs

