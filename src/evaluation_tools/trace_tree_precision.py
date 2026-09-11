from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from typing import Dict, List, Optional, Set, FrozenSet, Tuple
from uuid import UUID

from src.data_structures.process_tree_operator import Operator
from src.data_structures.process_tree import Node
from src.data_structures.event import Event
from src.data_structures.trace import Trace


# ============================================================
# PARTIAL ORDER REPRESENTATION
# ============================================================

@dataclass(frozen=True)
class POEvent:
    """
    Event inside a model-generated partial order.

    event_id is only relevant internally.
    label is the observable activity label.
    """

    event_id: int
    label: str


@dataclass(frozen=True)
class PartialOrder:
    """
    Immutable partial order.

    less:
        strict order relation x < y

    overlap:
        symmetric overlap relation x || y

    The relations are stored using event IDs.
    """

    events: FrozenSet[POEvent]
    less: FrozenSet[Tuple[int, int]]
    overlap: FrozenSet[Tuple[int, int]]

    def labels(self) -> FrozenSet[str]:
        return frozenset(
            e.label
            for e in self.events
            if e.label != "tau"
        )

    def predecessors(self, event_id: int) -> Set[int]:
        return {
            a
            for a, b in self.less
            if b == event_id
        }

    def successors(self, event_id: int) -> Set[int]:
        return {
            b
            for a, b in self.less
            if a == event_id
        }

    def is_before(self, a: int, b: int) -> bool:
        return (a, b) in self.less

    def is_overlap(self, a: int, b: int) -> bool:
        return (a, b) in self.overlap


# ============================================================
# EVENT FACTORY
# ============================================================

class EventFactory:

    def __init__(self):
        self._counter = 0

    def new(self, label: str) -> POEvent:
        result = POEvent(
            self._counter,
            label,
        )
        self._counter += 1
        return result


# ============================================================
# BASIC PARTIAL ORDER OPERATIONS
# ============================================================

def transitive_closure(
    less: Set[Tuple[int, int]]
) -> Set[Tuple[int, int]]:
    """
    Transitive closure of a strict relation.
    """

    result = set(less)

    changed = True

    while changed:
        changed = False

        current = list(result)

        for a, b in current:
            for c, d in current:

                if b == c and a != d:

                    edge = (a, d)

                    if edge not in result:
                        result.add(edge)
                        changed = True

    return result


def has_cycle(
    less: Set[Tuple[int, int]]
) -> bool:

    closure = transitive_closure(less)

    return any(
        a == b
        for a, b in closure
    )


def normalize_po(
    po: PartialOrder
) -> PartialOrder:
    """
    Normalize the strict order to its transitive closure and
    make overlap symmetric.
    """

    less = transitive_closure(
        set(po.less)
    )

    overlap = set(po.overlap)

    overlap |= {
        (b, a)
        for a, b in list(overlap)
    }

    # A pair cannot be both strict and overlapping.
    overlap = {
        pair
        for pair in overlap
        if pair not in less
        and (pair[1], pair[0]) not in less
    }

    return PartialOrder(
        events=frozenset(po.events),
        less=frozenset(less),
        overlap=frozenset(overlap),
    )


def empty_po() -> PartialOrder:
    return PartialOrder(
        events=frozenset(),
        less=frozenset(),
        overlap=frozenset(),
    )


def add_event(
    po: PartialOrder,
    event: POEvent,
) -> PartialOrder:

    return PartialOrder(
        events=frozenset(
            set(po.events) | {event}
        ),
        less=po.less,
        overlap=po.overlap,
    )


def copy_with_offset(
    po: PartialOrder,
    factory: EventFactory,
    event_map: Optional[Dict[int, int]] = None,
) -> Tuple[PartialOrder, Dict[int, int]]:
    """
    Create a structurally identical copy with fresh event IDs.

    Labels remain unchanged.
    """

    if event_map is None:
        event_map = {}

    mapping = {}

    for event in po.events:

        new_event = factory.new(
            event.label
        )

        mapping[event.event_id] = (
            new_event.event_id
        )

    new_events = {
        POEvent(
            mapping[event.event_id],
            event.label,
        )
        for event in po.events
    }

    new_less = {
        (
            mapping[a],
            mapping[b],
        )
        for a, b in po.less
    }

    new_overlap = {
        (
            mapping[a],
            mapping[b],
        )
        for a, b in po.overlap
    }

    return (
        PartialOrder(
            events=frozenset(new_events),
            less=frozenset(new_less),
            overlap=frozenset(new_overlap),
        ),
        mapping,
    )


# ============================================================
# PARTIAL ORDER COMPOSITION
# ============================================================

def compose_sequence(
    left: PartialOrder,
    right: PartialOrder,
) -> PartialOrder:
    """
    left -> right

    Every event of left occurs strictly before every event
    of right.
    """

    events = (
        set(left.events)
        | set(right.events)
    )

    less = (
        set(left.less)
        | set(right.less)
        | {
            (a.event_id, b.event_id)
            for a in left.events
            for b in right.events
        }
    )

    overlap = (
        set(left.overlap)
        | set(right.overlap)
    )

    return normalize_po(
        PartialOrder(
            events=frozenset(events),
            less=frozenset(less),
            overlap=frozenset(overlap),
        )
    )


def compose_parallel(
    left: PartialOrder,
    right: PartialOrder,
) -> PartialOrder:
    """
    Parallel operator:

    Every event from left overlaps every event from right.
    """

    events = (
        set(left.events)
        | set(right.events)
    )

    less = (
        set(left.less)
        | set(right.less)
    )

    overlap = (
        set(left.overlap)
        | set(right.overlap)
        | {
            (a.event_id, b.event_id)
            for a in left.events
            for b in right.events
        }
    )

    return normalize_po(
        PartialOrder(
            events=frozenset(events),
            less=frozenset(less),
            overlap=frozenset(overlap),
        )
    )


def compose_arbitrary(
    children: List[PartialOrder],
) -> Set[PartialOrder]:
    """
    Arbitrary order:

    Children are executed in an arbitrary order.

    Entire child blocks remain ordered.
    """

    result = set()

    for order in permutations(
        range(len(children))
    ):

        current = empty_po()

        for index in order:

            current = compose_sequence(
                current,
                children[index],
            )

        result.add(current)

    return result


def compose_interleaving(
    left: PartialOrder,
    right: PartialOrder,
) -> Set[PartialOrder]:
    """
    Interleaving:

    - no cross-child overlap
    - cross-child activities may occur in arbitrary order
    - internal orders are preserved
    """

    left_events = list(left.events)
    right_events = list(right.events)

    result = set()

    all_events = (
        left_events
        + right_events
    )

    for ordering in permutations(
        all_events
    ):

        position = {
            event.event_id: i
            for i, event in enumerate(ordering)
        }

        valid = True

        for a, b in (
            left.less | right.less
        ):

            if position[a] >= position[b]:
                valid = False
                break

        if not valid:
            continue

        less = (
            set(left.less)
            | set(right.less)
        )

        for a in left_events:

            for b in right_events:

                if (
                    position[a.event_id]
                    < position[b.event_id]
                ):
                    less.add(
                        (
                            a.event_id,
                            b.event_id,
                        )
                    )

                else:
                    less.add(
                        (
                            b.event_id,
                            a.event_id,
                        )
                    )

        po = normalize_po(
            PartialOrder(
                events=frozenset(all_events),
                less=frozenset(less),
                overlap=frozenset(
                    left.overlap
                    | right.overlap
                ),
            )
        )

        result.add(po)

    return result


def compose_concurrent(
    left: PartialOrder,
    right: PartialOrder,
) -> Set[PartialOrder]:
    """
    Concurrent:

    Cross-child events may be:

        a < b
        b < a
        a || b

    subject to acyclicity.
    """

    left_events = list(left.events)
    right_events = list(right.events)

    cross_pairs = [
        (a, b)
        for a in left_events
        for b in right_events
    ]

    result = set()

    for assignments in product(
        range(3),
        repeat=len(cross_pairs),
    ):

        less = (
            set(left.less)
            | set(right.less)
        )

        overlap = (
            set(left.overlap)
            | set(right.overlap)
        )

        for (a, b), relation in zip(
            cross_pairs,
            assignments,
        ):

            if relation == 0:

                less.add(
                    (
                        a.event_id,
                        b.event_id,
                    )
                )

            elif relation == 1:

                less.add(
                    (
                        b.event_id,
                        a.event_id,
                    )
                )

            else:

                overlap.add(
                    (
                        a.event_id,
                        b.event_id,
                    )
                )

                overlap.add(
                    (
                        b.event_id,
                        a.event_id,
                    )
                )

        if has_cycle(less):
            continue

        po = normalize_po(
            PartialOrder(
                events=frozenset(
                    set(left.events)
                    | set(right.events)
                ),
                less=frozenset(less),
                overlap=frozenset(overlap),
            )
        )

        result.add(po)

    return result


# ============================================================
# MODEL SEMANTICS
# ============================================================

class ProcessTreeSemantics:

    def __init__(
        self,
        root: Node,
        max_events: int,
        tau_label: str = "tau",
    ):
        self.root = root
        self.max_events = max_events
        self.tau_label = tau_label

        self.factory = EventFactory()

        self._cache = {}

    # --------------------------------------------------------
    # Public
    # --------------------------------------------------------

    def generate(self) -> Set[PartialOrder]:
        """
        Generate all observable model executions with at most
        max_events visible events.

        Silent tau events are removed afterwards.
        """

        raw = self._generate(
            self.root
        )

        result = set()

        for po in raw:

            projected = self.project_tau(po)

            if (
                self.visible_size(projected)
                <= self.max_events
            ):
                result.add(projected)

        return result

    # --------------------------------------------------------
    # Recursive semantics
    # --------------------------------------------------------

    def _generate(
        self,
        node: Node,
    ) -> Set[PartialOrder]:

        cache_key = id(node)

        if cache_key in self._cache:
            return self._cache[cache_key]

        # ----------------------------------------------------
        # Leaf
        # ----------------------------------------------------

        if node.is_leaf():

            event = self.factory.new(
                str(node.value)
            )

            po = PartialOrder(
                events=frozenset({event}),
                less=frozenset(),
                overlap=frozenset(),
            )

            result = {po}

            self._cache[cache_key] = result

            return result

        operator = node.value

        # ----------------------------------------------------
        # EXCLUSIVE
        # ----------------------------------------------------

        if operator == Operator.Exclusive:

            result = set()

            # Exactly one child.
            for child in node.children:
                result |= self._generate(child)

            self._cache[cache_key] = result

            return result

        # ----------------------------------------------------
        # SEQUENCE
        # ----------------------------------------------------

        if operator == Operator.Sequence:

            result = {
                empty_po()
            }

            for child in node.children:

                child_pos = self._generate(
                    child
                )

                new_result = set()

                for prefix in result:

                    for child_po in child_pos:

                        composed = compose_sequence(
                            prefix,
                            child_po,
                        )

                        if (
                            self.visible_size(composed)
                            <= self.max_events
                        ):
                            new_result.add(
                                composed
                            )

                result = new_result

            self._cache[cache_key] = result

            return result

        # ----------------------------------------------------
        # ARBITRARY
        # ----------------------------------------------------

        if operator == Operator.Arbitrary:

            child_languages = [
                self._generate(child)
                for child in node.children
            ]

            result = set()

            for selected in product(
                *child_languages
            ):

                for po in compose_arbitrary(
                    list(selected)
                ):

                    if (
                        self.visible_size(po)
                        <= self.max_events
                    ):
                        result.add(po)

            self._cache[cache_key] = result

            return result

        # ----------------------------------------------------
        # INTERLEAVING
        # ----------------------------------------------------

        if operator == Operator.Interleaving:

            result = {
                empty_po()
            }

            for child in node.children:

                child_pos = self._generate(
                    child
                )

                new_result = set()

                for prefix in result:

                    for child_po in child_pos:

                        if not prefix.events:

                            new_result.add(
                                child_po
                            )

                        else:

                            for po in compose_interleaving(
                                prefix,
                                child_po,
                            ):

                                if (
                                    self.visible_size(po)
                                    <= self.max_events
                                ):
                                    new_result.add(po)

                result = new_result

            self._cache[cache_key] = result

            return result

        # ----------------------------------------------------
        # CONCURRENT
        # ----------------------------------------------------

        if operator == Operator.Concurrent:

            result = {
                empty_po()
            }

            for child in node.children:

                child_pos = self._generate(
                    child
                )

                new_result = set()

                for prefix in result:

                    for child_po in child_pos:

                        if not prefix.events:

                            new_result.add(
                                child_po
                            )

                        else:

                            for po in compose_concurrent(
                                prefix,
                                child_po,
                            ):

                                if (
                                    self.visible_size(po)
                                    <= self.max_events
                                ):
                                    new_result.add(po)

                result = new_result

            self._cache[cache_key] = result

            return result

        # ----------------------------------------------------
        # PARALLEL
        # ----------------------------------------------------

        if operator == Operator.Parallel:

            result = {
                empty_po()
            }

            for child in node.children:

                child_pos = self._generate(
                    child
                )

                new_result = set()

                for prefix in result:

                    for child_po in child_pos:

                        if not prefix.events:

                            new_result.add(
                                child_po
                            )

                        else:

                            composed = compose_parallel(
                                prefix,
                                child_po,
                            )

                            if (
                                self.visible_size(composed)
                                <= self.max_events
                            ):
                                new_result.add(
                                    composed
                                )

                result = new_result

            self._cache[cache_key] = result

            return result

        # ----------------------------------------------------
        # LOOP
        # ----------------------------------------------------

        if operator == Operator.Loop:

            result = self._generate_loop(
                node
            )

            self._cache[cache_key] = result

            return result

        # ----------------------------------------------------
        # MULTI
        # ----------------------------------------------------

        if operator == Operator.Multi:

            if len(node.children) != 1:
                raise ValueError(
                    "Multi must have exactly one child."
                )

            child = node.children[0]

            child_pos = self._generate(
                child
            )

            result = set()

            # At least one instance.
            #
            # Since max_events is guaranteed to be int,
            # this range is type-safe.
            for number_of_instances in range(
                1,
                self.max_events + 1,
            ):

                for selected in product(
                    child_pos,
                    repeat=number_of_instances,
                ):

                    copies = []

                    for po in selected:

                        copy, _ = copy_with_offset(
                            po,
                            self.factory,
                        )

                        copies.append(copy)

                    current = copies[0]

                    for copy in copies[1:]:

                        current = compose_parallel(
                            current,
                            copy,
                        )

                    if (
                        self.visible_size(current)
                        <= self.max_events
                    ):
                        result.add(current)

            self._cache[cache_key] = result

            return result

        raise ValueError(
            f"Unsupported process tree operator: "
            f"{operator}"
        )

    # --------------------------------------------------------
    # LOOP
    # --------------------------------------------------------

    def _generate_loop(
        self,
        node: Node,
    ) -> Set[PartialOrder]:
        """
        Loop(A, B, C, ...)

        Semantics:

            A

            A B A
            A C A
            A B A C A
            A C A B A
            A B A B A
            ...

        Exactly ONE redo child is allowed between two
        consecutive executions of the first child.
        """

        if len(node.children) < 2:
            raise ValueError(
                "Loop requires at least two children."
            )

        body = node.children[0]

        redo_children = node.children[1:]

        body_language = self._generate(
            body
        )

        redo_languages = [
            self._generate(child)
            for child in redo_children
        ]

        # Every loop starts with A.
        current_results = set(
            body_language
        )

        result = set(
            current_results
        )

        # max_events is guaranteed to be int.
        for _ in range(
            self.max_events
        ):

            next_results = set()

            for prefix in current_results:

                for redo_language in redo_languages:

                    for redo_po in redo_language:

                        after_redo = compose_sequence(
                            prefix,
                            redo_po,
                        )

                        if (
                            self.visible_size(after_redo)
                            > self.max_events
                        ):
                            continue

                        for body_po in body_language:

                            complete_iteration = (
                                compose_sequence(
                                    after_redo,
                                    body_po,
                                )
                            )

                            if (
                                self.visible_size(
                                    complete_iteration
                                )
                                <= self.max_events
                            ):

                                next_results.add(
                                    complete_iteration
                                )

            if not next_results:
                break

            result |= next_results

            current_results = next_results

        return result

    # --------------------------------------------------------
    # Tau projection
    # --------------------------------------------------------

    def project_tau(
        self,
        po: PartialOrder,
    ) -> PartialOrder:
        """
        Remove tau events from a partial order.

        A < tau < B becomes A < B.
        """

        visible = {
            e
            for e in po.events
            if e.label != self.tau_label
        }

        visible_ids = {
            e.event_id
            for e in visible
        }

        closure = transitive_closure(
            set(po.less)
        )

        less = {
            (a, b)
            for a, b in closure
            if a in visible_ids
            and b in visible_ids
        }

        overlap = {
            (a, b)
            for a, b in po.overlap
            if a in visible_ids
            and b in visible_ids
        }

        return normalize_po(
            PartialOrder(
                events=frozenset(visible),
                less=frozenset(less),
                overlap=frozenset(overlap),
            )
        )

    def visible_size(
        self,
        po: PartialOrder,
    ) -> int:

        return sum(
            1
            for e in po.events
            if e.label != self.tau_label
        )


# ============================================================
# TRACE -> PARTIAL ORDER
# ============================================================

def trace_to_po(
    trace: Trace,
) -> PartialOrder:
    """
    Convert a user Trace into an immutable PartialOrder.

    Event IDs are preserved.

    The trace is NOT linearized.
    """

    events = {
        POEvent(
            event_id=_uuid_to_int(
                event.get_id()
            ),
            label=event.get_label(),
        )
        for event in trace.get_events()
    }

    def eid(event):
        return _uuid_to_int(
            event.get_id()
        )

    less = {
        (
            eid(a),
            eid(b),
        )
        for a, b in trace.get_strict_partial_order()
    }

    overlap = {
        (
            eid(a),
            eid(b),
        )
        for a, b in trace.get_overlapping_events()
    }

    return normalize_po(
        PartialOrder(
            events=frozenset(events),
            less=frozenset(less),
            overlap=frozenset(overlap),
        )
    )


def _uuid_to_int(
    value: UUID,
) -> int:
    return value.int


# ============================================================
# TAU PROJECTION FOR TRACES
# ============================================================

def project_trace_tau(
    po: PartialOrder,
    tau_label: str = "tau",
) -> PartialOrder:

    visible = {
        e
        for e in po.events
        if e.label != tau_label
    }

    visible_ids = {
        e.event_id
        for e in visible
    }

    closure = transitive_closure(
        set(po.less)
    )

    less = {
        (a, b)
        for a, b in closure
        if a in visible_ids
        and b in visible_ids
    }

    overlap = {
        (a, b)
        for a, b in po.overlap
        if a in visible_ids
        and b in visible_ids
    }

    return normalize_po(
        PartialOrder(
            events=frozenset(visible),
            less=frozenset(less),
            overlap=frozenset(overlap),
        )
    )


# ============================================================
# CANONICAL PREFIX REPRESENTATION
# ============================================================

def canonical_key(
    po: PartialOrder,
) -> Tuple:
    """
    Canonical representation of a labeled partial order.

    Events with different labels cannot be mapped to each other.

    Events with identical labels may be permuted.
    """

    events = list(po.events)

    groups: Dict[
        str,
        List[POEvent]
    ] = {}

    for event in events:

        groups.setdefault(
            event.label,
            []
        ).append(event)

    labels = sorted(groups)

    permutations_per_group = []

    for label in labels:

        group = groups[label]

        permutations_per_group.append(
            list(
                permutations(group)
            )
        )

    candidates = []

    for grouped_permutation in product(
        *permutations_per_group
    ):

        ordered_events = []

        for group in grouped_permutation:
            ordered_events.extend(group)

        relation_matrix = []

        for a in ordered_events:

            row = []

            for b in ordered_events:

                if a.event_id == b.event_id:

                    row.append("0")

                elif (
                    a.event_id,
                    b.event_id
                ) in po.less:

                    row.append("<")

                elif (
                    b.event_id,
                    a.event_id
                ) in po.less:

                    row.append(">")

                elif (
                    a.event_id,
                    b.event_id
                ) in po.overlap:

                    row.append("|")

                else:

                    row.append(".")

            relation_matrix.append(
                tuple(row)
            )

        candidate = (
            tuple(
                event.label
                for event in ordered_events
            ),
            tuple(relation_matrix),
        )

        candidates.append(candidate)

    return min(candidates)


# ============================================================
# PREFIX GENERATION
# ============================================================

def is_order_ideal(
    po: PartialOrder,
    subset: Set[int],
) -> bool:
    """
    A prefix is an order ideal:

        e in P and x < e
        => x in P
    """

    for a, b in po.less:

        if b in subset and a not in subset:
            return False

    return True


def all_order_ideal_prefixes(
    po: PartialOrder,
) -> List[PartialOrder]:
    """
    Generate all observable order-ideal prefixes.

    This does NOT linearize the trace.
    """

    events = list(po.events)

    n = len(events)

    result = []

    for mask in range(
        1 << n
    ):

        subset = {
            events[i].event_id
            for i in range(n)
            if mask & (1 << i)
        }

        if not is_order_ideal(
            po,
            subset,
        ):
            continue

        prefix_events = {
            e
            for e in events
            if e.event_id in subset
        }

        prefix_less = {
            (a, b)
            for a, b in po.less
            if a in subset
            and b in subset
        }

        prefix_overlap = {
            (a, b)
            for a, b in po.overlap
            if a in subset
            and b in subset
        }

        prefix = PartialOrder(
            events=frozenset(prefix_events),
            less=frozenset(prefix_less),
            overlap=frozenset(prefix_overlap),
        )

        result.append(
            normalize_po(prefix)
        )

    return result


# ============================================================
# OBSERVED EXTENSIONS
# ============================================================

@dataclass(frozen=True)
class Extension:
    """
    One observable event extending a prefix.

    The extension is represented by the complete canonical key
    of the resulting prefix.
    """

    extended_prefix_key: Tuple


def observed_extensions_for_trace(
    po: PartialOrder,
) -> Dict[
    Tuple,
    Set[Extension]
]:
    """
    Returns:

        prefix_key -> observed extensions

    For every order-ideal prefix P, every event e outside P
    whose predecessors are already in P gives one extension.
    """

    result: Dict[
        Tuple,
        Set[Extension]
    ] = {}

    events = list(po.events)

    for prefix in all_order_ideal_prefixes(po):

        prefix_ids = {
            e.event_id
            for e in prefix.events
        }

        prefix_key = canonical_key(
            prefix
        )

        for event in events:

            if event.event_id in prefix_ids:
                continue

            predecessors = po.predecessors(
                event.event_id
            )

            if not predecessors.issubset(
                prefix_ids
            ):
                continue

            extended_events = (
                set(prefix.events)
                | {event}
            )

            extended_ids = {
                e.event_id
                for e in extended_events
            }

            extended_less = {
                (a, b)
                for a, b in po.less
                if a in extended_ids
                and b in extended_ids
            }

            extended_overlap = {
                (a, b)
                for a, b in po.overlap
                if a in extended_ids
                and b in extended_ids
            }

            extended = normalize_po(
                PartialOrder(
                    events=frozenset(
                        extended_events
                    ),
                    less=frozenset(
                        extended_less
                    ),
                    overlap=frozenset(
                        extended_overlap
                    ),
                )
            )

            result.setdefault(
                prefix_key,
                set()
            ).add(
                Extension(
                    extended_prefix_key=canonical_key(
                        extended
                    )
                )
            )

    return result


# ============================================================
# LOG LANGUAGE
# ============================================================

class PartialOrderLog:

    def __init__(
        self,
        traces: List[Trace],
        tau_label: str = "tau",
    ):
        self.traces = traces
        self.tau_label = tau_label

        self.trace_pos = [
            project_trace_tau(
                trace_to_po(trace),
                tau_label=tau_label,
            )
            for trace in traces
        ]

        self.observed_extensions = (
            self._build_observed_language()
        )

    def _build_observed_language(
        self,
    ) -> Dict[
        Tuple,
        Set[Extension]
    ]:

        result: Dict[
            Tuple,
            Set[Extension]
        ] = {}

        for po in self.trace_pos:

            extensions = (
                observed_extensions_for_trace(
                    po
                )
            )

            for prefix_key, ext_set in (
                extensions.items()
            ):

                result.setdefault(
                    prefix_key,
                    set()
                ).update(
                    ext_set
                )

        return result

    def extensions(
        self,
        prefix_key: Tuple,
    ) -> Set[Extension]:

        return self.observed_extensions.get(
            prefix_key,
            set(),
        )

    def extensions_for_prefix(
        self,
        prefix_key: Tuple,
    ) -> Set[Extension]:

        return self.observed_extensions.get(
            prefix_key,
            set(),
        )


# ============================================================
# MODEL EXTENSIONS
# ============================================================

class ModelLanguage:

    def __init__(
        self,
        root: Node,
        max_events: int,
        tau_label: str = "tau",
    ):
        self.root = root
        self.max_events = max_events
        self.tau_label = tau_label

        semantics = ProcessTreeSemantics(
            root=root,
            max_events=max_events,
            tau_label=tau_label,
        )

        self.executions = semantics.generate()

        self.extensions = (
            self._build_extensions()
        )

    def _build_extensions(
        self,
    ) -> Dict[
        Tuple,
        Set[Extension]
    ]:

        result: Dict[
            Tuple,
            Set[Extension]
        ] = {}

        for execution in self.executions:

            prefixes = all_order_ideal_prefixes(
                execution
            )

            for prefix in prefixes:

                prefix_key = canonical_key(
                    prefix
                )

                prefix_ids = {
                    e.event_id
                    for e in prefix.events
                }

                for event in execution.events:

                    if event.event_id in prefix_ids:
                        continue

                    predecessors = (
                        execution.predecessors(
                            event.event_id
                        )
                    )

                    if not predecessors.issubset(
                        prefix_ids
                    ):
                        continue

                    extended_events = (
                        set(prefix.events)
                        | {event}
                    )

                    extended_ids = {
                        e.event_id
                        for e in extended_events
                    }

                    extended_less = {
                        (a, b)
                        for a, b in execution.less
                        if a in extended_ids
                        and b in extended_ids
                    }

                    extended_overlap = {
                        (a, b)
                        for a, b in execution.overlap
                        if a in extended_ids
                        and b in extended_ids
                    }

                    extended = normalize_po(
                        PartialOrder(
                            events=frozenset(
                                extended_events
                            ),
                            less=frozenset(
                                extended_less
                            ),
                            overlap=frozenset(
                                extended_overlap
                            ),
                        )
                    )

                    result.setdefault(
                        prefix_key,
                        set()
                    ).add(
                        Extension(
                            extended_prefix_key=canonical_key(
                                extended
                            )
                        )
                    )

        return result

    def extensions_for_prefix(
        self,
        prefix_key: Tuple,
    ) -> Set[Extension]:

        return self.extensions.get(
            prefix_key,
            set(),
        )


# ============================================================
# ESCAPING EDGES
# ============================================================

@dataclass
class EscapingEdgeResult:

    prefix_key: Tuple

    observed: Set[Extension]

    model: Set[Extension]

    escaping: Set[Extension]

    @property
    def number_of_observed(self):
        return len(self.observed)

    @property
    def number_of_model(self):
        return len(self.model)

    @property
    def number_of_escaping(self):
        return len(self.escaping)


class EscapingEdgesPrecision:

    def __init__(
        self,
        log: List[Trace],
        process_tree: Node,
        max_events: Optional[int] = None,
        tau_label: str = "tau",
    ):

        self.log = log
        self.process_tree = process_tree
        self.tau_label = tau_label

        # ----------------------------------------------------
        # Resolve max_events HERE.
        #
        # From this point onward max_events is guaranteed
        # to be an int.
        # ----------------------------------------------------

        if max_events is None:

            max_events = max(
                (
                    sum(
                        1
                        for e in trace.get_events()
                        if e.get_label() != tau_label
                    )
                    for trace in log
                ),
                default=0,
            )

        self.max_events: int = max_events

        # ----------------------------------------------------
        # Log language
        # ----------------------------------------------------

        self.log_language = PartialOrderLog(
            traces=log,
            tau_label=tau_label,
        )

        # ----------------------------------------------------
        # Model language
        #
        # max_events is now definitely int.
        # ----------------------------------------------------

        self.model_language = ModelLanguage(
            root=process_tree,
            max_events=self.max_events,
            tau_label=tau_label,
        )

    # --------------------------------------------------------
    # Escaping edges
    # --------------------------------------------------------

    def compute(
        self,
    ) -> List[EscapingEdgeResult]:

        all_prefixes = set(
            self.log_language.observed_extensions.keys()
        )

        results = []

        for prefix_key in all_prefixes:

            observed = (
                self.log_language.extensions_for_prefix(
                    prefix_key
                )
            )

            model = (
                self.model_language.extensions_for_prefix(
                    prefix_key
                )
            )

            escaping = model - observed

            results.append(
                EscapingEdgeResult(
                    prefix_key=prefix_key,
                    observed=observed,
                    model=model,
                    escaping=escaping,
                )
            )

        return results

    # --------------------------------------------------------
    # Aggregate score
    # --------------------------------------------------------

    def precision(self) -> float:

        results = self.compute()

        total_model_edges = sum(
            len(result.model)
            for result in results
        )

        total_escaping_edges = sum(
            len(result.escaping)
            for result in results
        )

        if total_model_edges == 0:
            return 1.0

        return (
            1.0
            - total_escaping_edges
            / total_model_edges
        )

    # --------------------------------------------------------
    # Detailed report
    # --------------------------------------------------------

    def report(self):

        results = self.compute()

        return {
            "precision": self.precision(),
            "number_of_prefixes": len(results),
            "number_of_model_edges": sum(
                len(r.model)
                for r in results
            ),
            "number_of_observed_edges": sum(
                len(r.observed)
                for r in results
            ),
            "number_of_escaping_edges": sum(
                len(r.escaping)
                for r in results
            ),
            "prefixes": results,
        }


# ============================================================
# HUMAN-READABLE EXTENSION DECODING
# ============================================================

def extension_to_text(
    extension: Extension,
) -> str:
    """
    The canonical key contains the complete extended prefix.

    This helper gives a compact textual representation.
    """

    labels, matrix = (
        extension.extended_prefix_key
    )

    parts = []

    for i, label in enumerate(labels):

        parts.append(
            f"{i}:{label}"
        )

    return (
        "events=["
        + ", ".join(parts)
        + "]"
    )


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Model:
    #
    #       XOR
    #      /   \
    #     A     B
    #
    # --------------------------------------------------------

    root = Node(
        Operator.Exclusive
    )

    root.add_child(
        Node("A")
    )

    root.add_child(
        Node("B")
    )

    # --------------------------------------------------------
    # Trace 1: A
    # --------------------------------------------------------

    a1 = Event("A")

    trace1 = Trace(
        events=[a1],
        transitive_reduced_strict_partial_order=[],
        strict_partial_order=[],
        overlapping_relation=[],
    )

    # --------------------------------------------------------
    # Trace 2: B
    # --------------------------------------------------------

    b1 = Event("B")

    trace2 = Trace(
        events=[b1],
        transitive_reduced_strict_partial_order=[],
        strict_partial_order=[],
        overlapping_relation=[],
    )

    # --------------------------------------------------------
    # Precision
    # --------------------------------------------------------

    evaluator = EscapingEdgesPrecision(
        log=[
            trace1,
            trace2,
        ],
        process_tree=root,
    )

    print(
        evaluator.report()
    )