from collections import deque
import copy

from data_structures.relations.minimum_self_distance_relation import MinimumSelfDistanceRelation
from src.data_structures.activity import Activity

def get_minimum_self_distance_relations(log):
    relationship_dict = {}

    # add every activity in the log as a key and as value add a dict with the keys distance and between
    for activity in log.get_activities():
        relationship_dict[activity] = {
            "minimum_self_distance": None,
            "activities_in_msd": None
        }

    for trace in log.get_traces():
        trace_dict = trace_self_distance_list(trace)
        #TODO sind in activities_in_msd activities oder events?
        for event, (distance, activities_in_msd) in trace_dict.items():
            old_distance = relationship_dict[event.get_activity()]["minimum_self_distance"]
        # if there is no distance for this activity yet add the new distance and the activities in msd
            if distance and not old_distance:
                relationship_dict[event.get_activity()]["minimum_self_distance"] = distance
                relationship_dict[event.get_activity()]["activities_in_msd"] = activities_in_msd
        # if the new distance is smaller than the old distance replace the distance and the activities in msd
            elif distance and distance < old_distance:
                relationship_dict[event.get_activity()]["minimum_self_distance"] = distance
                relationship_dict[event.get_activity()]["activities_in_msd"] = activities_in_msd
        # if the new distance is equal to the old distance add the new activities in msd
            elif distance and distance == old_distance:
                relationship_dict[event.get_activity()]["activities_in_msd"].update(activities_in_msd)

    msd_relation = []
    for activity, data in relationship_dict.items():
        #if data["distance"]: #TODO braucht es das?
            for target in data["activities_in_msd"]:
                msd_relation.append(MinimumSelfDistanceRelation(activity, target))
    #TODO WAS IST TARGET? ACTIVITY ODER EVENT?

    return msd_relation


# CODE FROM CHATGPT 08.07.2026

def trace_self_distance_list(trace):
    trace = copy.deepcopy(trace)

    events = trace.get_events()
    edges = trace.get_transitive_reduced_strict_partial_order()

    # Adjazenzliste
    adjacent_list = {e: [] for e in events}
    for edge in edges:
        adjacent_list[edge.get_first()].append(edge.get_second())

    result = {}

    for start in events:

        start_activity = start.get_activity()

        queue = deque([start])

        # kürzeste Distanz vom Start zu jedem Knoten
        distance = {start: 0}

        # alle Vorgänger auf einem kürzesten Pfad
        parents = {start: []}

        # alle Zielknoten mit minimaler Distanz
        best_distance = None
        best_targets = []

        while queue:

            node = queue.popleft()

            # Wenn wir schon eine Zielaktivität gefunden haben,
            # müssen längere Pfade nicht mehr betrachtet werden.
            if best_distance is not None and distance[node] >= best_distance:
                continue

            for nxt in adjacent_list[node]:

                new_dist = distance[node] + 1

                # erster Besuch
                if nxt not in distance:
                    distance[nxt] = new_dist
                    parents[nxt] = [node]
                    queue.append(nxt)

                # gleicher kürzester Weg
                elif new_dist == distance[nxt]:
                    parents[nxt].append(node)

                # gleiches Label gefunden
                if (
                    nxt != start
                    and nxt.get_activity() == start_activity
                ):
                    if best_distance is None:
                        best_distance = new_dist
                        best_targets = [nxt]
                    elif new_dist == best_distance:
                        best_targets.append(nxt)

        # --------------------------------------------------
        # Alle Aktivitäten auf allen kürzesten Pfaden sammeln
        # --------------------------------------------------

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

            # Start- und Zielaktivitäten entfernen
            visited_on_shortest.discard(start)
            for target in best_targets:
                visited_on_shortest.discard(target)

        result[start] = (
            best_distance,
            visited_on_shortest if best_distance is not None else None
        )

    return result