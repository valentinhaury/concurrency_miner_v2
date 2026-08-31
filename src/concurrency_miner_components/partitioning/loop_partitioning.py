from itertools import combinations, permutations

from src.concurrency_miner_components.helper_functions.partition_functions import merge_partitions

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
    partition_1 = set()
    partition_1 |= start_activities | end_activities
    partitions.append(partition_1)

    # create all other partitions from the non-start and non-end activities
    for activity in activities - partitions[0]:
        partitions.append({activity})

    # partitions 2-n should have no direct connections between them
    for a, b in combinations(activities - partitions[0], 2):
        if (a, b) in directly_follows_relations or (b, a) in directly_follows_relations:
            merge_partitions(a, b, partitions)

    # merge overlapping partitions
    for a, b in permutations(activities, 2):
        if (a, b) in overlapping_relations:
            _merge_loop_partitions(a, b, partitions)

    # merge partitions to p1 if they can be directly reached from a start-activity that is no end-activity
    for a_start in start_activities - end_activities:
        for b in activities - partitions[0]:
            if (a_start, b) in directly_follows_relations:
                _merge_loop_partitions(a_start, b, partitions)

    # merge partitions to p1 if an end-activity that is no start-activity can be directly reached from there
    for a_end in end_activities - start_activities:
        for b in activities - partitions[0]:
            if (b, a_end) in directly_follows_relations:
                _merge_loop_partitions(a_end, b, partitions)

    # merge partitions to p1 if from a partition one but not all start-activities can be reached
    # or if a partition can be reached from one but not all end-activities
    activities_to_merge = set()
    for partition in partitions:

        reaches_start_count = 0
        reached_by_end_count = 0

        # count how many start activities are reached from partition
        for a_start in start_activities:
            for b in partition:
                if (b, a_start) in directly_follows_relations:
                    reaches_start_count += 1
                    break # important break to not count start activities double

        # count from how many end activities partition is reached
        for a_end in end_activities:
            for b in partition:
                if (a_end, b) in directly_follows_relations:
                    reached_by_end_count += 1
                    break # important break to not count end activities double

        if 0 < reaches_start_count < len(start_activities):
            activities_to_merge.add(next(iter(partition)))
        elif 0 < reached_by_end_count < len(end_activities):
            activities_to_merge.add(next(iter(partition)))

    for activity in activities_to_merge:
        _merge_loop_partitions(next(iter(partitions[0])), activity, partitions)

    return partitions

