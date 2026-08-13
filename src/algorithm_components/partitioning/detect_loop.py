from itertools import combinations

from src.data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.algorithm_components.helper_functions.partition_functions import merge_partitions


def detect_loop(log):
    return len(create_loop_partitions(log)) > 1

def _merge_loop_partitions(activity_a, activity_b, partitions):
    # merge partitions but keep p1 at index 0
    if activity_a in partitions[0] or activity_b in partitions[0]:
        merge_partitions(activity_a, activity_b, partitions)
        partitions.insert(0, partitions.pop())
    else:
        merge_partitions(activity_a, activity_b, partitions)

def create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations):

    partitions = []

    # create partition 1 where all start and end activities are
    partition_1 = start_activities | end_activities
    partitions.append(partition_1)

    # create all other partitions from the non-start and non-end activities
    for activity in activities - partitions[0]:
        partitions.append({activity})
    # partitions 2-n should have no direct connections between them
    for a, b in combinations(activities - partitions[0], 2):
        if DirectlyFollowsRelation(a, b) in directly_follows_relations or DirectlyFollowsRelation(b, a) in directly_follows_relations:
            merge_partitions(a, b, partitions)

    # merge overlapping partitions
    for a, b in combinations(activities, 2):
        if OverlappingRelation(a, b) in overlapping_relations:
            _merge_loop_partitions(a, b, partitions)

    # merge partitions to p1 if they can be directly reached from a start-activity that is no end-activity
    for a_start in start_activities - end_activities:
        for b in activities - partitions[0]:
            if DirectlyFollowsRelation(a_start, b) in directly_follows_relations:
                _merge_loop_partitions(a_start, b, partitions)

    # merge partitions to p1 if an end-activity that is no start-activity can be directly reached from there
    for a_end in end_activities - start_activities:
        for b in activities - partitions[0]:
            if DirectlyFollowsRelation(b, a_end) in directly_follows_relations:
                _merge_loop_partitions(a_end, b, partitions)

    # merge partitions to p1 if from a partition one but not all start-activities can be reached
    # or if a partition can be reached from one but not all end-activities
    partitions_to_merge = []
    # loop over p2 - pn
    for i in range(1, len(partitions)):

        partition = partitions[i]

        reaches_start_count = 0
        reached_by_end_count = 0

        # count how many start activities are reached from partition
        for b in partition:
            for a_start in start_activities:
                if DirectlyFollowsRelation(b, a_start) in directly_follows_relations:
                    reaches_start_count += 1
                    break # important break to not count start activities double

        # count from how many end activities partition is reached
        for b in partition:
            for a_end in end_activities:
                if DirectlyFollowsRelation(a_end, b) in directly_follows_relations:
                    reached_by_end_count += 1
                    break # important break to not count end activities double

        if 0 < reaches_start_count < len(start_activities):
            partitions_to_merge.append(i)
        elif 0 < reached_by_end_count < len(end_activities):
            partitions_to_merge.append(i)

    # starts with the highest index, so that the smaller indices are not changed
    while partitions_to_merge:
        i = partitions_to_merge.pop()
        _merge_loop_partitions(partitions[0][0], partitions[i][0], partitions)

    return partitions

