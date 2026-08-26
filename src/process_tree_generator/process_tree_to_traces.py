from data_structures.event import Event
from src.process_tree_generator.simple_trace import SimpleTrace
from src.data_structures.process_tree_operator import Operator


def generate_traces(node):

## BASE CASE SINGLE ACTIVITY ------------------------------------------

    if not isinstance(node.value, Operator):
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

        result = [
            PartialOrderTrace(
                activities=frozenset(),
                edges=frozenset()
            )
        ]

        for child in node.children:

            child_traces = _generate(child)

            new_result = []

            for left in result:
                for right in child_traces:
                    new_result.append(
                        sequence(left, right)
                    )

            result = new_result

        return result

# ARBITRARY ORDER ------------------------------------------

    if operator == Operator.Arbitrary:
        return _generate_arbitrary(node)

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

    if operator == Operator.Loop:
        return _generate_loop(node)

def _generate_multi(node):
    children = node.children
    activity = children[0]
    single_activity_trace = SimpleTrace([Event(activity)], set())
    double_activity_trace = SimpleTrace([Event(activity), Event(activity)], set())
    triple_activity_trace = SimpleTrace([Event(activity), Event(activity), Event(activity)], set())
    return [single_activity_trace, double_activity_trace, triple_activity_trace]