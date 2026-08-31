from itertools import permutations

from src.data_structures.trace import Trace


def get_trace_from_simple_trace(simple_trace):
    events = simple_trace.events
    strict_partial_order = simple_trace.strict_partial_order

    transitive_reduced_strict_partial_order = set(strict_partial_order)
    for e1, e2, e3 in permutations(events, 3):
        if (e1, e2) in strict_partial_order and (e2, e3) in strict_partial_order and (e1, e3) in transitive_reduced_strict_partial_order:
            transitive_reduced_strict_partial_order.remove((e1, e3))

    overlapping_relation = set()
    for e1, e2 in permutations(events, 2):
        if (e1, e2) not in strict_partial_order and (e2, e1) not in strict_partial_order:
            overlapping_relation.add((e1, e2))
            overlapping_relation.add((e2, e1))

    return Trace(events, transitive_reduced_strict_partial_order, strict_partial_order, overlapping_relation)
