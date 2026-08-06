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
    changed = True
    while changed:
        changed = False
        for p1, p2 in combinations(trace_partitions, 2):
            if changed:
                break
            for t1, t2 in product(p1, p2):
                if not are_disjunct(t1, t2):
                    changed = True
                    p1.extend(p2)
                    trace_partitions.remove(p2)
                    break
    return trace_partitions

def are_disjunct(t1, t2):
        for a1, a2 in product(t1.get_activities_by_label(), t2.get_activities_by_label()):
            if a1.get_label() == a2.get_label():
                return False
        return True



