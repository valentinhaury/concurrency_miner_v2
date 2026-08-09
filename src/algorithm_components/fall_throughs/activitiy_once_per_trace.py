from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_concurrent

def create_activity_once_per_trace_partitions(traces, activities):
    activities_in_every_trace = set()
    activities_in_every_trace |= traces[0].get_activities()
    for trace in traces:
        activities_in_every_trace &= trace.get_activities()

    if activities_in_every_trace:
        partition1 = set()
        partition1.add(next(iter(activities_in_every_trace)))
        partition2 = set(activities - partition1)
        return [partition1, partition2]
    else:
        return [activities]

def get_activity_once_per_trace_sublogs(log, concurrent_partitions):
    return create_sublogs_concurrent(log, concurrent_partitions)