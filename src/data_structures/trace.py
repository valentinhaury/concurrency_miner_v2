from itertools import product, permutations

from data_structures.relations.transitiv_reduced_strict_partial_order_relation import \
    TransitivReducedStrictPartialOrder
from src.data_structures.relations.strict_partial_order_relation import StrictPartialOrder
from src.data_structures.activity import Activity
from data_structures.relations.relation import Relation
from data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from data_structures.relations.overlapping_relation import OverlappingRelation
from data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation

class Trace:
    def __init__(self, events, transitive_reduced_strict_partial_order):
        self.events = set(events)
        self.activities = set()
        for event in events:
            self.activities.add(event.get_activity())
        self.transitive_reduced_strict_partial_order = set(transitive_reduced_strict_partial_order)
        self.strict_partial_order = self._compute_transitive_closure()

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

    def __str__(self):
        if not self.events:
            return "(empty-trace)"
        trace_string = "(E{"
        if self.events:
            for event in self.events:
                trace_string += str(event) + ", "
            trace_string = trace_string[:-2]
        trace_string += "},(A{"
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

    def get_transitiv_reduced_strict_partial_order(self):
        return self.transitive_reduced_strict_partial_order

    def get_strict_partial_order(self):
        return self.strict_partial_order

    def get_start_activities(self):
        start_activities = set()
        for e1 in self.events:
            is_start = True
            for e2 in self.events:
                if TransitivReducedStrictPartialOrder(e2, e1) in self.transitive_reduced_strict_partial_order:
                    is_start = False
            if is_start:
                start_activities.add(e1.get_activity())
        return start_activities

    def get_end_activities(self):
        end_activities = set()
        for e1 in self.events:
            is_end = True
            for e2 in self.events:
                if TransitivReducedStrictPartialOrder(e1, e2) in self.transitive_reduced_strict_partial_order:
                    is_end = False
            if is_end:
                end_activities.add(e1.get_activity())
        return end_activities




    def get_directly_follows_relations(self):
        return self.directly_follows_relations

    def get_directly_follows_relations_by_label(self):
        dfg_by_label = []
        if self.directly_follows_relations:
            for relation in self.directly_follows_relations:
                if not relation.relation_exists_by_label(dfg_by_label):
                    dfg_by_label.append(Relation(Activity(relation.get_first_activity().get_label()), Activity(relation.get_second_activity().get_label()))) # Relation(Activity(relation.get_first_activity().get_label()), Activity(relation.get_second_activity().get_label()))
        return dfg_by_label

    def get_overlapping_relations_by_label(self):
        overlapping_by_label = []
        for relation in self.get_overlapping_relations_by_id():
            if not relation.relation_exists_by_label(overlapping_by_label):
                overlapping_by_label.append(Relation(Activity(relation.get_first_activity().get_label()), Activity(relation.get_second_activity().get_label())))
        return overlapping_by_label

    def get_overlapping_relations_by_id(self):
        eventually_follows_relations = self.get_eventually_follows_relations_by_id()
        return [
            OverlappingRelation(a1, a2)
            for a1, a2 in product(self.activities, repeat = 2)
            if not EventuallyFollowsRelation(a1, a2).relation_exists_by_id(eventually_follows_relations)
               and not EventuallyFollowsRelation(a2, a1).relation_exists_by_id(eventually_follows_relations)
               and not a1 == a2
        ]

    def get_eventually_follows_relations_by_label(self):
        eventually_follows_by_label = []
        for relation in self.get_eventually_follows_relations_by_id():
            if not relation.relation_exists_by_label(eventually_follows_by_label):
                eventually_follows_by_label.append(Relation(Activity(relation.get_first_activity().get_label()), Activity(relation.get_second_activity().get_label())))
        return eventually_follows_by_label

    def get_eventually_follows_relations_by_id(self):
        eventually_follows_relations = []
        for relation in self.directly_follows_relations:
           eventually_follows_relations.append(EventuallyFollowsRelation(relation.get_first_activity(), relation.get_second_activity()))

        added_relations = ["true"]
        while added_relations:
            added_relations = [
                EventuallyFollowsRelation(a1, a2)
                for a1, a2 in product(self.activities, repeat=2)
                for a3 in self.activities
                if not Relation(a1, a2).relation_exists_by_id(eventually_follows_relations)
                   and Relation(a1, a3).relation_exists_by_id(eventually_follows_relations)
                   and Relation(a3, a2).relation_exists_by_id(eventually_follows_relations)
            ]

            if added_relations:
                for relation in added_relations:
                    if not relation.relation_exists_by_id(eventually_follows_relations):
                        eventually_follows_relations.append(relation)
        return eventually_follows_relations



