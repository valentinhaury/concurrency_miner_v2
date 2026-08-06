import copy
from src.data_structures.activity import Activity
from data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation

def detect_single_activity(event_log):
    log = copy.deepcopy(event_log)
    activities = log.get_activities_by_label()
    if len(activities) > 1:
        return False
    traces = log.get_traces()
    for trace in traces:
        if len(trace.get_activities()) > 1:
            for a1 in trace.get_activities():
                for a2 in trace.get_activities():
                    if a1 != a2 and EventuallyFollowsRelation(a1, a2).relation_exists_by_label(trace.get_eventually_follows_relations()):
                        return False
    return True

def get_single_activity(log):
    activities = log.get_activities_by_label()
    if activities:
        return activities[0]
    else:
        return Activity("tau")
