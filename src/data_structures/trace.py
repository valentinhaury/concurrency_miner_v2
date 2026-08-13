from itertools import product, permutations

from src.data_structures.relations.transitive_reduced_strict_partial_order import \
    TransitiveReducedStrictPartialOrder
from src.data_structures.relations.strict_partial_order import StrictPartialOrder
from src.data_structures.relations.overlapping_relation import OverlappingRelation


class Trace:
    def __init__(self, events, transitive_reduced_strict_partial_order, strict_partial_order, overlapping_relation):
        self.events = set(events)
        self.activities = set()
        for event in events:
            self.activities.add(event.get_label())
        self.transitive_reduced_strict_partial_order = set(transitive_reduced_strict_partial_order)
        self.strict_partial_order = set(strict_partial_order)
        self.overlapping_relations = set(overlapping_relation)

    def __str__(self):
        if not self.events:
            return "(empty-trace)"
        trace_string = "(E{"
        if self.events:
            for event in self.events:
                trace_string += str(event) + ", "
            trace_string = trace_string[:-2]
        trace_string += "}, A{"
        if self.activities:
            for activity in self.activities:
                trace_string += str(activity) + ", "
            trace_string = trace_string[:-2]
        trace_string += "}, R{"
        if self.transitive_reduced_strict_partial_order:
            for relation in self.transitive_reduced_strict_partial_order:
                trace_string += str(relation[0]) + ">" + str(relation[1]) + ", "
            trace_string = trace_string[:-2]
        trace_string += "})"
        return trace_string

    def get_events(self):
        return self.events

    def get_activities(self):
        return self.activities

    def get_transitive_reduced_strict_partial_order(self):
        return self.transitive_reduced_strict_partial_order

    def get_strict_partial_order(self):
        return self.strict_partial_order

    def get_overlapping_relations_trace(self):
        return self.overlapping_relations

    def get_directly_follows(self):
        directly_follows = set()
        for r in self.transitive_reduced_strict_partial_order:
            directly_follows.add((r[0].get_label(), r[1].get_label()))
        return directly_follows

    def get_start_activities(self):
        start_activities = set()
        for e in self.events:
            if any(y == e for _, y in self.transitive_reduced_strict_partial_order):
                start_activities.add(e.get_label())
        return start_activities

    def get_end_activities(self):
        end_activities = set()
        for e in self.events:
            if any(y == e for y, _ in self.transitive_reduced_strict_partial_order):
                end_activities.add(e.get_label())
        return end_activities




    #not needed right now
    def _compute_transitive_closure(self):
        closure = set()
        for relation in self.transitive_reduced_strict_partial_order:
            closure.add((relation[0], relation[1]))
        changed = True
        while changed:
            changed = False
            for e1, e2, e3 in permutations(self.events, 3):
                relation = (e1, e3)
                if ((e1, e2) in closure and
                        (e2, e3) in closure and
                        relation not in closure):
                    closure.add(relation)
                    changed = True
        return closure