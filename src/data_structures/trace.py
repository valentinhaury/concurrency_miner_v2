from itertools import product, permutations

from src.data_structures.relations.transitive_reduced_strict_partial_order import \
    TransitiveReducedStrictPartialOrder
from src.data_structures.relations.strict_partial_order import StrictPartialOrder
from src.data_structures.relations.overlapping_relation import OverlappingRelation


class Trace:
    def __init__(self, events, transitive_reduced_strict_partial_order):
        self.events = set(events)
        self.activities = set()
        for event in events:
            self.activities.add(event.get_activity())
        self.transitive_reduced_strict_partial_order = set(transitive_reduced_strict_partial_order)
        self.strict_partial_order = self._compute_transitive_closure()

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
                trace_string += str(relation) + ", "
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

    def get_start_activities(self):
        start_activities = set()
        for e1 in self.events:
            is_start = True
            for e2 in self.events:
                if TransitiveReducedStrictPartialOrder(e2, e1) in self.transitive_reduced_strict_partial_order:
                    is_start = False
            if is_start:
                start_activities.add(e1.get_activity())
        return start_activities

    def get_end_activities(self):
        end_activities = set()
        for e1 in self.events:
            is_end = True
            for e2 in self.events:
                if TransitiveReducedStrictPartialOrder(e1, e2) in self.transitive_reduced_strict_partial_order:
                    is_end = False
            if is_end:
                end_activities.add(e1.get_activity())
        return end_activities

    def get_overlapping_relations_trace(self):
        overlapping_relations = set()
        for e1, e2 in product(self.events, repeat=2):
            if not StrictPartialOrder(e1, e2) in self.strict_partial_order \
                and not StrictPartialOrder(e2, e1) in self.strict_partial_order \
                and not e1 == e2:
                overlapping_relations.add(OverlappingRelation(e1.get_activity(), e2.get_activity()))

        return overlapping_relations

    def get_overlapping_events_relations(self):
        overlapping_relations = set()
        for e1, e2 in product(self.events, repeat=2):
            if not StrictPartialOrder(e1, e2) in self.strict_partial_order \
                and not StrictPartialOrder(e2, e1) in self.strict_partial_order \
                and not e1 == e2:
                overlapping_relations.add(OverlappingRelation(e1, e2))

        return overlapping_relations


    def _compute_transitive_closure(self):
        closure = set()
        for relation in self.transitive_reduced_strict_partial_order:
            closure.add(StrictPartialOrder(relation.get_first(), relation.get_second()))
        changed = True
        while changed:
            changed = False
            for e1, e2, e3 in permutations(self.events, 3):
                relation = StrictPartialOrder(e1, e3)
                if (StrictPartialOrder(e1, e2) in closure and
                        StrictPartialOrder(e2, e3) in closure and
                        relation not in closure):
                    closure.add(relation)
                    changed = True
        return closure