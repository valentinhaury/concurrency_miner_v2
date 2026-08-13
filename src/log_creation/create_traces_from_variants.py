from src.data_structures.event import Event
from src.data_structures.trace import Trace

def create_traces_from_variants(
        variants
):
    result = []
    for variant_entries in variants.values():
        for variant, traces in variant_entries:
            for _ in range(len(traces)):

                event_map = {}

                for label, event_ids in variant.events.items():
                    for event_id in event_ids:
                        event_map[event_id] = Event(
                            label=label
                        )

                transitive_reduced_partial_order = set()
                for _, relations in variant.directly_follows.items():
                    for source_id, target_id in relations:
                        transitive_reduced_partial_order.add(
                                (event_map[source_id], event_map[target_id])
                        )

                partial_order = set()
                for _, relations in variant.follows.items():
                    for source_id, target_id in relations:
                        partial_order.add(
                            (event_map[source_id], event_map[target_id])
                        )

                overlapping_relations = set()
                for _, relations in variant.concurrency_pairs.items():
                    for source_id, target_id in relations:
                        overlapping_relations.add(
                            (event_map[source_id], event_map[target_id])
                        )

                new_trace = Trace(
                    events=set(event_map.values()),
                    transitive_reduced_strict_partial_order=transitive_reduced_partial_order,
                    strict_partial_order=partial_order,
                    overlapping_relation=overlapping_relations
                )

                result.append(new_trace)

    return result