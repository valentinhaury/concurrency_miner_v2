import copy
from itertools import combinations

from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation
from src.algorithm_components.helper_functions.partition_functions import merge_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_sequential

def get_sequence_sublogs(log, sequence_partitions, eventually_follows_relations):
    return _sort_sublogs(create_sublogs_sequential(log, sequence_partitions), eventually_follows_relations)

def _sort_sublogs(sublogs, eventually_follows_relations):
    n = len(sublogs)
    for i in range(n):
      for j in range(i + 1, n):
        if _follows(sublogs[i],sublogs[j], eventually_follows_relations):
          sublogs[i], sublogs[j] = sublogs[j], sublogs[i]

    return sublogs

def _follows(log_a, log_b, eventually_follows_relations):
    for a1 in log_a.get_activities():
        for a2 in log_b.get_activities():
            if EventuallyFollowsRelation(a2, a1) in eventually_follows_relations:
                return True
            elif EventuallyFollowsRelation(a1, a2) in eventually_follows_relations:
                return False
    return False

def create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations):

    partitions = []
    for activity in activities:
        new_partition = set()
        new_partition.add(activity)
        partitions.append(new_partition)

    for a, b in combinations(activities, 2):
        # merge partitions if activities are overlapping in log
        if OverlappingRelation(a, b) in overlapping_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are pairwise reachable in log
        if EventuallyFollowsRelation(a, b) in eventually_follows_relations and EventuallyFollowsRelation(b, a) in eventually_follows_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are pairwise not-reachable in log
        if EventuallyFollowsRelation(a, b) not in eventually_follows_relations and EventuallyFollowsRelation(b, a) not in eventually_follows_relations:
            merge_partitions(a, b, partitions)

    return partitions