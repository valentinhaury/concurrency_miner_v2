from itertools import combinations

from src.data_structures.relations.minimum_self_distance_relation import MinimumSelfDistanceRelation
from src.data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.algorithm_components.helper_functions.partition_functions import merge_partitions
from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_concurrent


def get_interleaving_sublogs(log, interleaving_partitions):
    return create_sublogs_concurrent(log, interleaving_partitions)

def create_interleaving_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations, minimum_self_distance_relations):
    partitions = []
    for activity in activities:
        new_partition = set()
        new_partition.add(activity)
        partitions.append(new_partition)

    for a, b in combinations(activities, 2):
        # merge partitions if activities are overlapping in log
        if OverlappingRelation(a, b) in overlapping_relations:
            merge_partitions(a, b, partitions)
        # merge partitions if activities are not-fully pairwise connected in log
        if (not DirectlyFollowsRelation(a, b) in directly_follows_relations) or (not DirectlyFollowsRelation(b, a) in directly_follows_relations):
            merge_partitions(a, b, partitions)
        # merge partitions if activities are in minimum self distance relation in log
        if MinimumSelfDistanceRelation(a, b) in minimum_self_distance_relations or MinimumSelfDistanceRelation(b, a) in minimum_self_distance_relations:
            merge_partitions(a, b, partitions)

    # merge partitions with no start or no end activity to an arbitrary partition
    changed = True
    while len(partitions) > 1 and changed:
        changed = False
        for i, partition in enumerate(partitions):
            if partition.isdisjoint(start_activities) or partition.isdisjoint(end_activities):
                if i == 0:
                    merge_partitions(next(iter(partition)), next(iter(partitions[1])), partitions)
                else:
                    merge_partitions(next(iter(partition)), next(iter(partitions[0])), partitions)
                changed = True
                break

    return partitions

