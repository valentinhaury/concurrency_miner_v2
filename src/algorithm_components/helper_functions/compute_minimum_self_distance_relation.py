from collections import deque
import copy

from src.data_structures.relations.minimum_self_distance_relation import MinimumSelfDistanceRelation

def compute_minimum_self_distance_relations(activities, traces):
    activity_msd_dictionary = {}
    print(str(activities))
    # add every activity in the log as a key and as value add a dict with the keys distance and between
    for activity in activities:
        activity_msd_dictionary[activity] = {
            "minimum_self_distance": None,
            "activities_in_msd": None
        }

    for trace in traces:
        trace_dict = trace_self_distance_list(trace)
        for event, (distance, events_in_msd) in trace_dict.items():
            old_distance = activity_msd_dictionary[event.get_label()]["minimum_self_distance"]
            if not distance:
                continue
            activities_in_msd = set()
            for event_msd in events_in_msd:
                activities_in_msd.add(event_msd.get_label())
        # if there is no distance for this activity yet add the new distance and the activities in msd
            if not old_distance:
                activity_msd_dictionary[event.get_label()]["minimum_self_distance"] = distance
                activity_msd_dictionary[event.get_label()]["activities_in_msd"] = activities_in_msd
        # if the new distance is smaller than the old distance replace the distance and the activities in msd
            elif distance < old_distance:
                activity_msd_dictionary[event.get_label()]["minimum_self_distance"] = distance
                activity_msd_dictionary[event.get_label()]["activities_in_msd"] = activities_in_msd
        # if the new distance is equal to the old distance add the new activities in msd
            elif distance == old_distance:
                activity_msd_dictionary[event.get_label()]["activities_in_msd"].update(activities_in_msd)

    msd_relation = set()

    for activity, data in activity_msd_dictionary.items():
        if not data["activities_in_msd"]:
            continue
        for target in data["activities_in_msd"]:
            msd_relation.add((activity, target))

    return msd_relation

def trace_self_distance_list(trace):
    trace = copy.deepcopy(trace)

    events = trace.get_events()
    transitive_reduced_strict_partial_order = trace.get_transitive_reduced_strict_partial_order()

    adjacent_list = {e: [] for e in events}
    for relation in transitive_reduced_strict_partial_order:
        adjacent_list[relation[0]].append(relation[1])

    result = {}

    for start in events:

        start_activity = start.get_label()

        queue = deque([start])

        # dict with key(event) and the shortest distance from start to that event
        distance = {start: 0}

        # dict with key(event) and a list of parents that are parent on a shortest path
        parents = {start: []}

        # shortest distance to a target (different event with same activity) and all targets with minimal distance
        best_distance = None
        best_targets = []

        while queue:

            node = queue.popleft()

            # Skip paths that are longer than an already completed path
            if best_distance is not None and distance[node] >= best_distance:
                continue

            for nxt in adjacent_list[node]:

                new_dist = distance[node] + 1

                # first time finding this node
                if nxt not in distance:
                    distance[nxt] = new_dist
                    parents[nxt] = [node]
                    queue.append(nxt)

                # same shortest path -> add parent node to parents
                elif new_dist == distance[nxt]:
                    parents[nxt].append(node)

                # found same label
                if (
                    nxt != start
                    and nxt.get_label() == start_activity
                ):
                    if best_distance is None:
                        best_distance = new_dist
                        best_targets = [nxt]
                    elif new_dist == best_distance:
                        best_targets.append(nxt)

        # collect events on all shortest paths
        visited_on_shortest = set()

        def collect(node):
            if node == start:
                return

            visited_on_shortest.add(node)

            for p in parents[node]:
                collect(p)

        if best_distance is not None:
            for target in best_targets:
                collect(target)

            # remove start and target event
            visited_on_shortest.discard(start)
            for target in best_targets:
                visited_on_shortest.discard(target)

        result[start] = (
            best_distance,
            visited_on_shortest if best_distance is not None else None
        )

    return result