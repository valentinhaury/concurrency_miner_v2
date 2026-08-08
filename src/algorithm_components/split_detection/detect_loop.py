import copy
from itertools import product, combinations

from data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.data_structures.log import Log
from src.data_structures.trace import Trace
from src.data_structures.relations.transitive_reduced_strict_partial_order import TransitiveReducedStrictPartialOrder
from src.algorithm_components.helper_functions.helper_functions import direct_connected_id, overlapping
from src.algorithm_components.helper_functions.partition_functions import merge_partitions


def detect_loop(log):
    return len(create_loop_partitions(log)) > 1

def get_loop_sublogs(log):
    partitions = create_loop_partitions(log)
    sublogs = []
    for partition in partitions:
        new_sublog = Log([])
        for trace in log.get_traces():
            trace_directly_follows_relation = trace.get_directly_follows_relations()
            trace_overlapping_relation = trace.get_overlapping_relations()

            activities = trace.get_activities()
            partition_activities = []
            for activity in activities:
                if activity.activity_exists_by_label(partition):
                    partition_activities.append(activity)

            while partition_activities:
                new_trace = Trace()
                changed = True
                while changed:
                    changed = False
                    saved_activities = []
                    for i in range(len(partition_activities)):
                        a1 = partition_activities.pop()
                        added = False
                        if not new_trace.get_activities():
                            new_trace.add_activity(a1)
                            added = True
                        else:
                            for a2 in new_trace.get_activities():
                                if direct_connected_id(a1, a2, trace_directly_follows_relation) or overlapping(a1, a2, trace_overlapping_relation):
                                    new_trace.add_activity(a1)
                                    changed = True
                                    added = True
                                    break
                        if not added:
                            saved_activities.append(a1)
                    partition_activities = saved_activities
                new_trace_activities = new_trace.get_activities()
                for relation in trace_directly_follows_relation:
                    if relation.get_first_activity() in new_trace_activities and relation.get_second_activity() in new_trace_activities:
                        new_trace.add_directly_follows_relation(relation)
                new_sublog.add_trace(new_trace)
        sublogs.append(new_sublog)

    return sublogs

def _merge_loop_partitions(activity_a, activity_b, partitions):
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
    for a, b in activities - partitions[0]:
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
#   or if a partition can be reached from one but not all end-activities
    partitions_to_merge = []
    for i in range(1, len(partitions)):

        partition = partitions[i]

        reaches_start_count = 0
        reached_by_end_count = 0

        for a_start in start_activities:
            for b in partition:
                if DirectlyFollowsRelation(b, a_start) in directly_follows_relations:
                    reaches_start_count += 1
                    break

        for a_end in end_activities:
            for b in partition:
                if DirectlyFollowsRelation(a_end, b) in directly_follows_relations:
                    reached_by_end_count += 1
                    break

        if 0 < reaches_start_count < len(start_activities):
            partitions_to_merge.append(i)
        elif 0 < reached_by_end_count < len(end_activities):
            partitions_to_merge.append(i)

    # starts with the highest index, so that the smaller indices are not changed
    while partitions_to_merge:
        i = partitions_to_merge.pop()
        _merge_loop_partitions(partitions[0][0], partitions[i][0], partitions)

    return partitions

