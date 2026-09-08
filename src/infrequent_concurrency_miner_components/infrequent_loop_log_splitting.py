from concurrency_miner_components.helper_functions.sublog_functions import create_new_trace_from_event_partition
from data_structures.event import Event
from data_structures.trace import Trace


def create_filtered_sublogs_loop(log, partitions):
    sublogs = []
    partition_1_activities = partitions[0]
    # for every partition create a new sub-log
    for partition in partitions:
        sub_log = _create_partition_loop_sub_log(log, partition, partition_1_activities)
        if sub_log:
            sublogs.append(sub_log)

    return sublogs

def _create_partition_loop_sub_log(log, partition, partition_1_activities):
    sub_log = []
    # for every trace create 1-n traces in every sub-log
    # for example for trace (a b a b a)
    # if partition is {a} create traces (a) (a) (a)
    # if partition is {b} create traces (b) (b)
    for old_trace in log:

        # new events are old events that are present in the partition
        partition_events = {event for event in old_trace.events if event.get_label() in partition}

        if partition & partition_1_activities:
            # if the activities from partition_1 are not in the trace, add an empty trace
            if not partition_events:
                sub_log.append(Trace({Event("tau")}, set(), set(), set()))
            # if partition_1 is not starting and or ending the trace, add an empty trace
            else:
                if old_trace.get_start_activities().isdisjoint(partition_1_activities):
                    sub_log.append(Trace({Event("tau")}, set(), set(), set()))
                if old_trace.get_end_activities().isdisjoint(partition_1_activities):
                    sub_log.append(Trace({Event("tau")}, set(), set(), set()))

        # as long as there are events from the trace left new traces are created
        while partition_events:
            # initiate new trace events
            new_trace_events = set()
            new_trace_events.add(partition_events.pop())

            # update the new_trace_events until all direct connected or overlapping events from this partition are added
            changed = True
            while changed and partition_events:
                changed = False
                for (e1, e2) in old_trace.get_transitive_reduced_strict_partial_order():
                    if e1 in new_trace_events and e2 in partition_events:
                        new_trace_events.add(e2)
                        partition_events.remove(e2)
                        changed = True
                    if e2 in new_trace_events and e1 in partition_events:
                        new_trace_events.add(e1)
                        partition_events.remove(e1)
                        changed = True

                for (e1, e2) in old_trace.get_overlapping_events():
                    if e1 in new_trace_events and e2 in partition_events:
                        new_trace_events.add(e2)
                        partition_events.remove(e2)
                        changed = True

            # remove all events that are added to the new trace
            partition_events = partition_events - new_trace_events

            # add the new trace to the sublog
            new_trace = create_new_trace_from_event_partition(new_trace_events, old_trace)
            sub_log.append(
                new_trace
            )
    return sub_log