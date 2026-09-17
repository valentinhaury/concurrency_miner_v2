from itertools import combinations, permutations
from functools import lru_cache

from src.data_structures.process_tree_operator import Operator

BEFORE = "before"
AFTER = "after"
OVERLAP = "overlap"


class TraceTreeMatcher:

    def __init__(self, trace):
        self.trace = trace

    def trace_fits_tree(self, tree):
        events = frozenset(self.trace.get_events())
        return self.matches(tree, events)

    @lru_cache(maxsize=None)
    def matches(self, node, events):
        if node.value == Operator.Multi:
            return self.match_multi_instance(node, events)

        if len(node.children) == 0:
            return self.match_leaf(node, events)

        if node.value == Operator.Sequence:
            return self.match_sequence(node, events)

        if node.value == Operator.Arbitrary:
            return self.match_arbitrary_order(node, events)

        if node.value == Operator.Interleaving:
            return self.match_interleaving(node, events)

        if node.value == Operator.Concurrent:
            return self.match_concurrent(node, events)

        if node.value == Operator.Parallel:
            return self.match_parallel(node, events)

        if node.value == Operator.Loop:
            return self.match_loop(node, events)

        if node.value == Operator.Exclusive:
            return self.match_exclusive(node, events)

        raise ValueError(f"Unknown operator: {node.value}")

    def match_leaf(self, node, events):
        # Silent activity / epsilon transition
        if node.value == "tau":
            return len(events) == 0

        # Normale Activity benötigt genau ein Event
        if len(events) != 1:
            return False

        event = next(iter(events))

        return event.get_label() == node.value

    def match_multi_instance(self, node, events):
        if len(node.children) != 1:
            raise ValueError(
                "MultiInstance must have exactly one child."
            )

        child = node.children[0]

        # Child muss ein Leaf sein
        if len(child.children) != 0:
            raise ValueError(
                "MultiInstance child must be an activity."
            )

        if child.value == "tau":
            raise ValueError(
                "MultiInstance child cannot be tau."
            )

        # At least one event
        if len(events) == 0:
            return False

        # Alle Events müssen dieselbe Activity sein
        if not all(
            event.get_label() == child.value
            for event in events
        ):
            return False

        events = list(events)

        # Jede Instanz muss mit jeder anderen überlappen
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                if self.relation(events[i], events[j]) != OVERLAP:
                    return False

        return True

    def match_sequence(self, node, events):
        children = node.children

        for subsets in self.partitions_for_children(
            events,
            children
        ):
            valid = True

            # Jedes Child muss seinen Teil matchen
            for child, subset in zip(children, subsets):
                if not self.matches(child, subset):
                    valid = False
                    break

            if not valid:
                continue

            # Zeitliche Reihenfolge prüfen
            for i in range(len(subsets)):
                for j in range(i + 1, len(subsets)):
                    if not self.all_before(
                        subsets[i],
                        subsets[j]
                    ):
                        valid = False
                        break

                if not valid:
                    break

            if valid:
                return True

        return False

    def match_arbitrary_order(self, node, events):
        children = node.children

        for ordered_children in permutations(children):

            for subsets in self.partitions_for_children(
                events,
                ordered_children
            ):
                valid = True

                for child, subset in zip(
                    ordered_children,
                    subsets
                ):
                    if not self.matches(child, subset):
                        valid = False
                        break

                if not valid:
                    continue

                # Die gewählte Reihenfolge muss zeitlich
                # tatsächlich vorhanden sein.
                for i in range(len(subsets)):
                    for j in range(i + 1, len(subsets)):
                        if not self.all_before(
                            subsets[i],
                            subsets[j]
                        ):
                            valid = False
                            break

                    if not valid:
                        break

                if valid:
                    return True

        return False

    def match_interleaving(self, node, events):

        children = node.children

        for subsets in self.partitions_for_children(
            events,
            children
        ):
            if not all(
                self.matches(child, subset)
                for child, subset in zip(children, subsets)
            ):
                continue

            valid = True

            for i in range(len(subsets)):
                for j in range(i + 1, len(subsets)):
                    if not self.all_non_overlapping(
                        subsets[i],
                        subsets[j]
                    ):
                        valid = False
                        break

                if not valid:
                    break

            if valid:
                return True

        return False

    def match_concurrent(self, node, events):
        children = node.children

        for subsets in self.partitions_for_children(
            events,
            children
        ):
            if all(
                self.matches(child, subset)
                for child, subset in zip(children, subsets)
            ):
                return True

        return False

    def match_parallel(self, node, events):
        children = node.children

        for subsets in self.partitions_for_children(
            events,
            children
        ):
            if not all(
                self.matches(child, subset)
                for child, subset in zip(children, subsets)
            ):
                continue

            valid = True

            for i in range(len(subsets)):
                for j in range(i + 1, len(subsets)):
                    if not self.all_overlap(
                        subsets[i],
                        subsets[j]
                    ):
                        valid = False
                        break

                if not valid:
                    break

            if valid:
                return True

        return False

    def match_loop(self, node, events):
        children = node.children

        if len(children) < 2:
            raise ValueError(
                "Loop must have at least two children."
            )

        body = children[0]
        redo_children = children[1:]

        return self.match_loop_recursive(
            body,
            redo_children,
            events
        )

    def match_loop_recursive(
        self,
        body,
        redo_children,
        events
    ):
        # --------------------------------------------------------
        # Fall 1:
        # Der aktuelle Body beendet den Loop.
        # --------------------------------------------------------

        if self.matches(body, events):
            return True

        # --------------------------------------------------------
        # Wir brauchen mindestens einen Redo-Branch.
        # --------------------------------------------------------

        if len(redo_children) == 0:
            return False

        # --------------------------------------------------------
        # Zuerst Events für den aktuellen Body auswählen.
        #
        # Der Body darf bei tau auch {} bekommen.
        # --------------------------------------------------------

        for body_subset, remaining_after_body in \
                self.split_for_child(events, body):

            if not self.matches(body, body_subset):
                continue

            # ----------------------------------------------------
            # Danach einen Redo-Child auswählen.
            # ----------------------------------------------------

            for redo_child in redo_children:

                for redo_subset, remaining_after_redo in \
                        self.split_for_child(
                            remaining_after_body,
                            redo_child
                        ):

                    if not self.matches(
                        redo_child,
                        redo_subset
                    ):
                        continue

                    # ------------------------------------------------
                    # Schutz vor endlosen tau -> tau -> tau ...
                    #
                    # Mindestens ein Event muss in diesem Loop-Zyklus
                    # verbraucht worden sein.
                    # ------------------------------------------------

                    consumed = (
                        len(body_subset)
                        + len(redo_subset)
                    )

                    if consumed == 0:
                        continue

                    # ------------------------------------------------
                    # Nach dem Redo muss wieder der Body kommen.
                    # ------------------------------------------------

                    if self.match_loop_recursive(
                        body,
                        redo_children,
                        remaining_after_redo
                    ):
                        return True

        return False

    def match_exclusive(self, node, events):
        for child in node.children:
            if self.matches(child, events):
                return True

        return False

    def partitions_for_children(self, events, children):
        events = tuple(events)

        if len(children) == 0:
            if len(events) == 0:
                yield tuple()
            return

        if len(children) == 1:
            child = children[0]

            if self.can_be_empty(child):
                yield (frozenset(events),)

            elif len(events) > 0:
                yield (frozenset(events),)

            return

        first_child = children[0]
        remaining_children = children[1:]

        # Darf dieses Child {} bekommen?
        first_can_be_empty = self.can_be_empty(first_child)

        min_size = 0 if first_can_be_empty else 1

        # Wie viele Events müssen mindestens für die restlichen
        # Children reserviert werden?
        required_for_rest = sum(
            0 if self.can_be_empty(child) else 1
            for child in remaining_children
        )

        max_size = len(events) - required_for_rest

        for size in range(
            min_size,
            max_size + 1
        ):
            for subset in combinations(events, size):

                first_subset = frozenset(subset)

                remaining_events = (
                    frozenset(events) - first_subset
                )

                for rest in self.partitions_for_children(
                    remaining_events,
                    remaining_children
                ):
                    yield (first_subset,) + rest

    def split_for_child(self, events, child):
        events = tuple(events)

        if self.can_be_empty(child):

            # Leere Teilmenge
            yield (
                frozenset(),
                frozenset(events)
            )

            # Zusätzlich alle nichtleeren Teilmengen
            for size in range(1, len(events) + 1):
                for subset in combinations(events, size):
                    subset = frozenset(subset)

                    yield (
                        subset,
                        frozenset(events) - subset
                    )

        else:

            # Normales Child muss mindestens ein Event erhalten
            for size in range(1, len(events) + 1):
                for subset in combinations(events, size):
                    subset = frozenset(subset)

                    yield (
                        subset,
                        frozenset(events) - subset
                    )

    def can_be_empty(self, node):
        if len(node.children) == 0:
            return node.value == "tau"

        return False

    def relation(self, e1, e2):
        if e1 == e2:
            return None

        order = self.trace.get_strict_partial_order()
        overlap = self.trace.get_overlapping_events()

        if (e1, e2) in order:
            return BEFORE

        if (e2, e1) in order:
            return AFTER

        if (e1, e2) in overlap:
            return OVERLAP

        if (e2, e1) in overlap:
            return OVERLAP

        return OVERLAP

    def all_before(self, events_a, events_b):
        return all(
            self.relation(a, b) == BEFORE
            for a in events_a
            for b in events_b
        )

    def all_overlap(self, events_a, events_b):
        return all(
            self.relation(a, b) == OVERLAP
            for a in events_a
            for b in events_b
        )

    def all_non_overlapping(self, events_a, events_b):
        return all(
            self.relation(a, b) in {
                BEFORE,
                AFTER
            }
            for a in events_a
            for b in events_b
        )