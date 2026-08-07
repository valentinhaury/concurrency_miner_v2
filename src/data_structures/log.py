from src.algorithm_components.helper_functions.compute_minimum_self_distance_relation import compute_minimum_self_distance_relations
from src.data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation
from src.data_structures.relations.directly_follows_relation import DirectlyFollowsRelation

class Log:
    def __init__(self, traces=None):
        if traces is None:
            traces = []
        self.traces = traces

    def __str__(self):
        if not self.traces:
            return "(empty-log)"
        string = "("
        for trace in self.traces:
            string += str(trace) + ",    "
        string = string[:-5] + ")"
        return string

    # TRACES

    def add_trace(self, trace):
        self.traces.append(trace)

    def get_traces(self):
        return self.traces

    # ACTIVITIES

    def get_activities(self):
        activities = set()
        for trace in self.traces:
            activities.update(trace.get_activities())
        return activities

    def get_start_activities(self):
        start_activities = set()
        for trace in self.traces:
            start_activities.update(trace.get_start_activities())
        return start_activities

    def get_end_activities(self):
        end_activities = set()
        for trace in self.traces:
            end_activities.update(trace.get_end_activities())
        return end_activities

    # RELATIONS

    def get_directly_follows_relations(self):
        directly_follows_relations = set()
        for trace in self.traces:
            for spo in trace.get_transitive_reduced_strict_partial_order():
                directly_follows_relations.add(DirectlyFollowsRelation(spo.get_first().get_activity(), spo.get_second().get_activity()))
        return directly_follows_relations

    def get_eventually_follows_relations(self):
        eventually_follows_relations = set()
        for trace in self.traces:
            for spo in trace.get_strict_partial_order():
                eventually_follows_relations.add(EventuallyFollowsRelation(spo.get_first().get_activity(), spo.get_second().get_activity()))
        return eventually_follows_relations

    def get_overlapping_relations(self):
        overlapping_relations = set()
        for trace in self.traces:
            overlapping_relations.update(trace.get_overlapping_relations_trace())
        return overlapping_relations

    def get_minimum_self_distance_relations(self):
        return compute_minimum_self_distance_relations(self)