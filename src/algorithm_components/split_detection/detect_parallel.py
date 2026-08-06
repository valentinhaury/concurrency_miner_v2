import copy
from itertools import combinations, product
from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.algorithm_components.helper_functions.partition_functions import connect_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_concurrent


def detect_parallel(log):
    return len(create_parallel_partitions(log)) > 1

def get_parallel_sublogs(log):
    partitions = create_parallel_partitions(log)
    return create_sublogs_concurrent(log, partitions)

def create_parallel_partitions(event_log):
    log = copy.deepcopy(event_log)
    activities = log.get_activities_by_label()
    traces = log.get_traces()
    partitions = []

    # initialize partitions
    while activities:
        new_partition = [activities.pop()]
        partitions.append(new_partition)

    # add all partitions if not every activity is overlapping every activity
    changed = True
    while changed:
        changed = False
        for p1, p2 in combinations(partitions, 2):
            for a, b in product(p1, p2):
                for trace in traces:
                    if not (OverlappingRelation(a, b).relation_exists_by_label(trace.get_overlapping_relations())
                        or OverlappingRelation(b, a).relation_exists_by_label(trace.get_overlapping_relations())):
                        changed = True
                        break
                if changed: break
            if changed:
                connect_partitions(p1[0], p2[0], partitions)
                break


    return partitions

