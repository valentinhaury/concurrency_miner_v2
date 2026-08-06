import copy
from data_structures.relations.overlapping_relation import OverlappingRelation


def get_multi_instance_activities(event_log):
    log = copy.deepcopy(event_log)
    multi_instance_activities = []
    for activity in log.get_activities_by_label():
        if OverlappingRelation(activity, activity).relation_exists_by_label(log.get_overlapping_relations()):
            multi_instance_activities.append(activity)
    return multi_instance_activities