from concurrency_miner_components.helper_functions.sublog_functions import create_new_trace_from_event_partition

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

        # create new trace from old trace with the partitioned events
        new_trace = create_new_trace_from_event_partition(new_trace_events, old_trace)

        sublogs[greatest_number_index].append(
            new_trace
        )

    return sublogs