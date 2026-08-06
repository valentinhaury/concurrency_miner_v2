import copy
from itertools import combinations
from data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation
from src.algorithm_components.helper_functions.helper_functions import overlapping_partitions, \
    eventually_connected_in_only_one_direction_partitions
from src.algorithm_components.helper_functions.partition_functions import connect_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_sequential


def detect_sequence(log):
    return len(create_sequence_partitions(log)) > 1

def get_sequence_sublogs(log):
    partitions = create_sequence_partitions(log)

    return _sort_sublogs(create_sublogs_sequential(log, partitions), log.get_eventually_follows_relations())

def _sort_sublogs(sublogs, eventually_follows_relations):
    n = len(sublogs)
    for i in range(n-1):
      swapped = False
      for j in range(n-i-1):
        if _follows(sublogs[j],sublogs[j+1], eventually_follows_relations):
          sublogs[j], sublogs[j+1] = sublogs[j+1], sublogs[j]
          swapped = True
      if not swapped:
        break

    return sublogs

def _follows(log_a, log_b, eventually_follows_relations):
    for a1 in log_a.get_activities_by_label():
        for a2 in log_b.get_activities_by_label():
            if EventuallyFollowsRelation(a2, a1).relation_exists_by_label(eventually_follows_relations):
                return True
            elif EventuallyFollowsRelation(a1, a2).relation_exists_by_label(eventually_follows_relations):
                return False
    return False



def create_sequence_partitions(event_log):
    log = copy.deepcopy(event_log)
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities_by_label()

    partitions = []

    while activities:
        new_partition = [activities.pop()]
        partitions.append(new_partition)

    # connect partitions with overlapping activities
    changed = True
    while changed:
        changed = False
        for p1, p2 in combinations(partitions, 2):
            if overlapping_partitions(p1, p2, overlapping_relations):
                connect_partitions(p1[0], p2[0], partitions)
                changed = True
                break

    # connect partitions that are eventually connected in both directions or in no direction
    changed = True
    while changed:
        changed = False
        for p1, p2 in combinations(partitions, 2):
            if not eventually_connected_in_only_one_direction_partitions(p1, p2, eventually_follows_relations):
                connect_partitions(p1[0], p2[0], partitions)
                changed = True
                break

    return partitions