import copy
from itertools import product, combinations
from src.data_structures.log import Log


def detect_exclusive(log):
    return len(create_exclusive_choice_partitions(log)) > 1

def get_exclusive_choice_sublogs(log):
    partitions = create_exclusive_choice_partitions(log)
    sublogs = []
    for partition in partitions:
        sublogs.append(Log(partition))
    return sublogs

def create_exclusive_choice_partitions(event_log):
    log = copy.deepcopy(event_log)
    traces = log.get_traces()
    if len(traces) == 0:
        return []
    if len(traces) == 1:
        return [[traces.pop()]]

    trace_partitions = []
    while traces:
        trace = traces.pop()
        trace_partitions.append([trace])

    for t1, t2 in combinations(log.get_traces(), 2):
        if not t1.get_activities().isdisjoint(t2.get_activities()):
            trace_partitions = _merge_trace_partitions(t1, t2, trace_partitions)

    return trace_partitions


def _merge_trace_partitions(t1, t2, trace_partitions):
    partition1 = []
    partition2 = []
    for partition in trace_partitions:
        if t1 in partition:
            partition1 = partition
            break

    for partition in trace_partitions:
        if t2 in partition:
            partition2 = partition
            break
    trace_partitions.remove(partition1)
    trace_partitions.remove(partition2)
    partition1.extend(partition2)
    trace_partitions.append(partition1)
    return trace_partitions



