import copy
import uuid
from enum import Enum
from itertools import product, permutations

from data_structures.event import Event
from data_structures.process_tree_operator import Operator
from src.process_tree_generator.simple_trace import SimpleTrace


def generate_traces(node):

## BASE CASE SINGLE ACTIVITY ------------------------------------------

    if not isinstance(node.value, Enum):
        activity = node.value
        single_activity_trace = SimpleTrace([Event(activity)], set())
        return [single_activity_trace]

    operator = node.value

## MULTI INSTANCE ------------------------------------------
    # if partition {a} return [a] [a || a] [a || a || a]
    if operator == Operator.Multi:
        return _generate_multi(node)

## only one child
    if len(node.children) == 1:
        if not operator == Operator.Loop:
            return generate_traces(node.children[0])

## EXCLUSIVE CHOICE ------------------------------------------
    if operator == Operator.Exclusive:
        result = []

        for child in node.children:
            result.extend(
                generate_traces(child)
            )

        return result

## Prepare trace partitions
    trace_partitions = []  # liste of list of traces.
    for child in node.children:
        child_traces = generate_traces(child)
        trace_partitions.append(child_traces)

# SEQUENCE ------------------------------------------

    if operator == Operator.Sequence:
        return _generate_sequence(trace_partitions)

# ARBITRARY ORDER ------------------------------------------

    if operator == Operator.Arbitrary:
        permutated_traces = [list(p) for p in permutations(trace_partitions)] # list of permutated lists of trace-partitions
        resulting_traces = []
        for trace_list in permutated_traces:
            resulting_traces.extend(_generate_sequence(trace_list))
        return resulting_traces

# INTERLEAVING ------------------------------------------

    if operator == Operator.Interleaving:
        return _generate_interleaving(trace_partitions)

# CONCURRENT ------------------------------------------

    if operator == Operator.Concurrent:
            return _generate_concurrent(trace_partitions)

# PARALLEL ------------------------------------------

    if operator == Operator.Parallel:
            return _generate_parallel(trace_partitions)

# LOOP ------------------------------------------
    # if partitions {a},{b},{c} return [a] [a < b < a] [a < c < a] [a < b < a < b < a] [a < b < a < c < a] [a < c < a < b < a] [a < c < a < c < a]
    if operator == Operator.Loop:
        result = []

        first_partition = trace_partitions.pop(0)

        first_partition_2 = copy.deepcopy(first_partition)
        for trace in first_partition_2:
            for event in trace.events:
                event.id = uuid.uuid4()

        first_partition_3 = copy.deepcopy(first_partition)
        for trace in first_partition_3:
            for event in trace.events:
                event.id = uuid.uuid4()

        for trace in first_partition:
            result.append(trace)
        for partition in trace_partitions:
            double_loop = [first_partition, partition, first_partition_2]
            result.extend(_generate_sequence(double_loop))
        for p1, p2 in product(trace_partitions, trace_partitions):

            p2 = copy.deepcopy(p2)
            for trace in p2:
                for event in trace.events:
                    event.id = uuid.uuid4()

            triple_loop = [first_partition, p1, first_partition_2, p2, first_partition_3]
            result.extend(_generate_sequence(triple_loop))
        return result


def _generate_multi(node):
    children = node.children
    activity = children[0]
    single_activity_trace = SimpleTrace([Event(activity)], set())
    double_activity_trace = SimpleTrace([Event(activity), Event(activity)], set())
    triple_activity_trace = SimpleTrace([Event(activity), Event(activity), Event(activity)], set())
    return [single_activity_trace, double_activity_trace, triple_activity_trace]

def _generate_sequence(trace_partitions):
    result = []
    for combination in product(*trace_partitions):
        new_trace = SimpleTrace(set(), set())
        for trace in combination:
            for event in trace.events:
                new_trace.add_event(event)
            for strict_partial_order in trace.strict_partial_order:
                new_trace.add_strict_partial_order(strict_partial_order)
        remaining_events = set(new_trace.events)
        for trace in combination:
            old_trace_events = trace.events
            remaining_events -= old_trace_events
            for e1, e2 in product(old_trace_events, remaining_events):
                new_trace.add_strict_partial_order((e1, e2))
        new_trace.compute_closure()
        result.append(new_trace)
    return result

def _generate_interleaving(trace_partitions):
    resulting_traces = []
    while trace_partitions:
        if not resulting_traces:
            resulting_traces = trace_partitions.pop()
        else:
            trace_partition = trace_partitions.pop()
            new_resulting_traces = []
            for t1, t2 in product(resulting_traces, trace_partition):
                new_trace_events = t1.events | t2.events
                for strict_partial_order in _all_combinations_interleaving(t1.events, t2.events, t1.strict_partial_order, t2.strict_partial_order):
                    new_trace = SimpleTrace(new_trace_events, strict_partial_order)
                    new_resulting_traces.append(new_trace)
            resulting_traces = new_resulting_traces
    return resulting_traces

def _generate_concurrent(trace_partitions):
    resulting_traces = []
    while trace_partitions:
        if not resulting_traces:
            resulting_traces = trace_partitions.pop()
        else:
            trace_partition = trace_partitions.pop()
            new_resulting_traces = []
            for t1, t2 in product(resulting_traces, trace_partition):
                new_trace_events = t1.events | t2.events
                for strict_partial_order in _all_combinations_concurrent(t1.events, t2.events, t1.strict_partial_order, t2.strict_partial_order):
                    new_trace = SimpleTrace(new_trace_events, strict_partial_order)
                    new_resulting_traces.append(new_trace)
            resulting_traces = new_resulting_traces
    return resulting_traces

def _generate_parallel(trace_partitions):
    resulting_traces = []
    while trace_partitions:
        if not resulting_traces:
            resulting_traces = trace_partitions.pop()
        else:
            trace_partition = trace_partitions.pop()
            new_resulting_traces = []
            for t1, t2 in product(resulting_traces, trace_partition):
                new_trace_events = t1.events | t2.events
                new_trace_strict_partial_order = t1.strict_partial_order | t2.strict_partial_order
                new_resulting_traces.append(SimpleTrace(new_trace_events, new_trace_strict_partial_order))
            resulting_traces = new_resulting_traces
    return resulting_traces

def _all_combinations_interleaving(A, B, relations_A, relations_B):
    A = set(A)
    B = set(B)

    base = set(relations_A) | set(relations_B)

    # Alle A-B-Paare, die noch orientiert werden müssen
    cross_pairs = [(a, b) for a in A for b in B]

    results = []

    def has_path(relations, start, target):
        """
        Prüft, ob es in relations bereits einen gerichteten
        Pfad von start nach target gibt.
        """
        visited = set()
        stack = [start]

        while stack:
            x = stack.pop()

            if x == target:
                return True

            if x in visited:
                continue

            visited.add(x)

            for u, v in relations:
                if u == x:
                    stack.append(v)

        return False

    def creates_cycle(relations, x, y):
        """
        x < y hinzufügen wäre genau dann ein Zyklus,
        wenn bereits ein Pfad von y nach x existiert.
        """
        return has_path(relations, y, x)

    def preserves_parallelism(relations):
        """
        Prüft, dass innerhalb von A und B keine ursprünglich
        parallelen Elemente vergleichbar geworden sind.
        """

        for X, original_relations in [
            (A, relations_A),
            (B, relations_B)
        ]:
            original_relations = set(original_relations)

            for x in X:
                for y in X:
                    if x == y:
                        continue

                    # Waren x und y ursprünglich parallel?
                    if (
                            (x, y) not in original_relations
                            and (y, x) not in original_relations
                    ):
                        # Sind sie jetzt vergleichbar?
                        if (
                                has_path(relations, x, y)
                                or has_path(relations, y, x)
                        ):
                            return False

        return True

    def backtrack(i, relations):
        # Alle Cross-Relations wurden orientiert
        if i == len(cross_pairs):
            if preserves_parallelism(relations):
                results.append(set(relations))
            return

        a, b = cross_pairs[i]

        # Möglichkeit 1: a < b
        if not creates_cycle(relations, a, b):
            relations.add((a, b))

            if preserves_parallelism(relations):
                backtrack(i + 1, relations)

            relations.remove((a, b))

        # Möglichkeit 2: b < a
        if not creates_cycle(relations, b, a):
            relations.add((b, a))

            if preserves_parallelism(relations):
                backtrack(i + 1, relations)

            relations.remove((b, a))

    backtrack(0, base)

    return results


def _all_combinations_concurrent(A, B, relations_A, relations_B):
    A = set(A)
    B = set(B)

    base = set(relations_A) | set(relations_B)

    # Alle Cross-Paare
    cross_pairs = [(a, b) for a in A for b in B]

    results = []

    def has_path(relations, start, target):
        """Gibt True zurück, wenn start -> ... -> target existiert."""
        visited = set()
        stack = [start]

        while stack:
            x = stack.pop()

            if x == target:
                return True

            if x in visited:
                continue

            visited.add(x)

            for u, v in relations:
                if u == x:
                    stack.append(v)

        return False

    def creates_cycle(relations, x, y):
        """
        Prüft, ob das Hinzufügen von x < y einen Zyklus erzeugen würde.
        """
        return has_path(relations, y, x)

    def preserves_parallelism(relations, parallel_pairs):
        """
        Prüft, dass weder ursprüngliche noch explizit gesetzte
        Parallelitäten durch Transitivität aufgehoben werden.
        """

        # Ursprüngliche Parallelitäten in A und B
        for X, original_relations in [
            (A, relations_A),
            (B, relations_B)
        ]:
            original_relations = set(original_relations)

            for x in X:
                for y in X:
                    if x == y:
                        continue

                    # Nur wirklich ursprünglich parallele Paare betrachten
                    if (
                            (x, y) not in original_relations
                            and (y, x) not in original_relations
                    ):
                        if (
                                has_path(relations, x, y)
                                or has_path(relations, y, x)
                        ):
                            return False

        # Explizit parallel gesetzte Cross-Paare
        for a, b in parallel_pairs:
            if (
                    has_path(relations, a, b)
                    or has_path(relations, b, a)
            ):
                return False

        return True

    def backtrack(i, relations, parallel_pairs):

        # Alle Cross-Paare verarbeitet
        if i == len(cross_pairs):
            results.append(set(relations))
            return

        a, b = cross_pairs[i]

        # -----------------------------------------
        # Fall 1: a < b
        # -----------------------------------------

        if not creates_cycle(relations, a, b):

            relations.add((a, b))

            if preserves_parallelism(relations, parallel_pairs):
                backtrack(
                    i + 1,
                    relations,
                    parallel_pairs
                )

            relations.remove((a, b))

        # -----------------------------------------
        # Fall 2: b < a
        # -----------------------------------------

        if not creates_cycle(relations, b, a):

            relations.add((b, a))

            if preserves_parallelism(relations, parallel_pairs):
                backtrack(
                    i + 1,
                    relations,
                    parallel_pairs
                )

            relations.remove((b, a))

        # -----------------------------------------
        # Fall 3: a || b
        # -----------------------------------------

        parallel_pairs.add((a, b))

        if preserves_parallelism(relations, parallel_pairs):
            backtrack(
                i + 1,
                relations,
                parallel_pairs
            )

        parallel_pairs.remove((a, b))

    backtrack(0, base, set())

    return results

