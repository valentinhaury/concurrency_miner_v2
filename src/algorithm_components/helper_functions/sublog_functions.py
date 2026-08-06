import copy
from itertools import combinations

from data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation
from src.data_structures.log import Log
from src.data_structures.trace import Trace

def get_log_without_activity(event_log, activity):
    log = copy.deepcopy(event_log)
    activity_label = activity.get_label()
    new_log = Log()
    for trace in log.get_traces():
        new_trace = Trace()
        #add all activities that have a different label then the removed activity
        for a1 in trace.get_activities():
            if a1.get_label() != activity_label:
                new_trace.add_activity(a1)
        #add all relations between the other activities
        for relation in trace.get_directly_follows_relations():
            if relation.get_first_activity().get_label() != activity_label and relation.get_second_activity().get_label() != activity_label:
                new_trace.add_directly_follows_relation(relation)
        #add relations, so that activities are connected that were previously connected through the removed activity
        for r1, r2 in combinations(trace.get_directly_follows_relations(), 2):
            if r1.get_second_activity().get_label() == activity_label and r1.get_second_activity() == r2.get_first_activity():
                new_trace.add_directly_follows_relation(DirectlyFollowsRelation(r1.get_first_activity(), r2.get_second_activity()))
        new_log.add_trace(new_trace)
    return new_log

def create_sublogs_concurrent(log, partitions):
    sublogs = []
    for partition in partitions:
        sub_log = []
        for trace in log.get_traces():
            new_trace = Trace()
            eventually_follows_relation_id = trace.get_eventually_follows_relations_by_id()
            for activity in trace.activities:
                if activity.activity_exists_by_label(partition):
                    new_trace.add_activity(activity)
            for relation in trace.get_directly_follows_relations():
                if relation.get_first_activity().activity_exists_by_label(new_trace.get_activities()) and relation.get_second_activity().activity_exists_by_label(new_trace.get_activities()):
                    new_trace.add_directly_follows_relation(relation)
            for a1 in new_trace.get_activities():
                for a2 in new_trace.get_activities():
                    if EventuallyFollowsRelation(a1, a2).relation_exists_by_id(eventually_follows_relation_id):
                        for a3 in new_trace.get_activities():
                            if  not (EventuallyFollowsRelation(a1, a3).relation_exists_by_id(eventually_follows_relation_id)
                                    and EventuallyFollowsRelation(a3, a2).relation_exists_by_id(eventually_follows_relation_id))\
                                and not DirectlyFollowsRelation(a1, a2).relation_exists_by_id(new_trace.get_directly_follows_relations()):
                                new_trace.add_directly_follows_relation(DirectlyFollowsRelation(a1, a2))
            sub_log.append(new_trace)
        sublogs.append(Log(sub_log))

    return sublogs


def create_sublogs_sequential(log, partitions):
    sublogs = []
    for partition in partitions:
        sub_log = []
        for trace in log.get_traces():
            new_trace = Trace()
            for activity in trace.activities:
                if activity.activity_exists_by_label(partition):
                    new_trace.add_activity(activity)
            for relation in trace.get_directly_follows_relations():
                if relation.get_first_activity().activity_exists_by_label(new_trace.get_activities()) and relation.get_second_activity().activity_exists_by_label(new_trace.get_activities()):
                    new_trace.add_directly_follows_relation(relation)
            sub_log.append(new_trace)
        sublogs.append(Log(sub_log))

    return sublogs
