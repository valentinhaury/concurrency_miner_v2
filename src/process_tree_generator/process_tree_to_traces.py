import copy
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

    if operator == Operator.Multi:
        return _generate_multi(node)

## EXCLUSIVE CHOICE ------------------------------------------
    if operator == Operator.Exclusive:
        result = []

        for child in node.children:
            result.extend(
                generate_traces(child)
            )

        return result

# SEQUENCE ------------------------------------------

    if operator == Operator.Sequence:
        trace_partitions = []  # liste of list of traces.
        for child in node.children:
            child_traces = generate_traces(child)
            trace_partitions.append(child_traces)
        return _generate_sequence(trace_partitions)

# ARBITRARY ORDER ------------------------------------------

    if operator == Operator.Arbitrary:
        trace_partitions = []  # list of trace-partitions
        for child in node.children:
            child_traces = generate_traces(child)
            trace_partitions.append(child_traces)
        permutated_traces = [list(p) for p in permutations(trace_partitions)] # list of permutated lists of trace-partitions
        resulting_traces = []
        for trace_list in permutated_traces:
            resulting_traces.extend(_generate_sequence(trace_list))
        return resulting_traces

# INTERLEAVING ------------------------------------------

    if operator == Operator.Interleaving:
        return _generate_interleaving(node)

# CONCURRENT ------------------------------------------

    if operator == Operator.Concurrent:
            return _generate_concurrent(node)

# PARALLEL ------------------------------------------

    if operator == Operator.Parallel:
            return _generate_parallel(node)

# LOOP ------------------------------------------
    # if partitions {a},{b},{c} return [a] [a b a] [a c a] [a b a b a] [a b a c a] [a c a b a] [a c a c a]
    if operator == Operator.Loop:
        return _generate_loop(node)

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



