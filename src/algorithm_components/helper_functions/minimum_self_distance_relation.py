from collections import deque
import copy
from src.data_structures.activity import Activity
from src.data_structures.relations.relation import Relation


def get_minimum_self_distance_relations(log):
    relationship_dict = {}

    for activity in log.get_activities_by_label():
        relationship_dict[activity.get_label()] = {
            "distance": None,
            "between": None
        }

    for trace in log.get_traces():
        trace_dict = trace_self_distance_list(trace)
        for act, (distance, relation) in trace_dict.items():
            old_distance = relationship_dict[act.get_label()]["distance"]
            if distance and not old_distance:
                relationship_dict[act.get_label()]["distance"] = distance
                relationship_dict[act.get_label()]["between"] = relation
            elif distance and distance < old_distance:
                relationship_dict[act.get_label()]["distance"] = distance
                relationship_dict[act.get_label()]["between"] = relation
            elif distance and distance == old_distance:
                relationship_dict[act.get_label()]["between"].extend(relation)

    msd_relation = []
    for activity, items in relationship_dict.items():
        if items["distance"]:
            for target in items["between"]:
                msd_relation.append(Relation(Activity(activity), target))

    return msd_relation






# CODE FROM CHATGPT 08.07.2026

def trace_self_distance_list(trace):
    trace = copy.deepcopy(trace)

    activities = trace.get_activities()
    edges = trace.get_directly_follows_relations()

    # Adjazenzliste
    graph = {a: [] for a in activities}
    for edge in edges:
        graph[edge.get_first_activity()].append(edge.get_second_activity())

    result = {}

    for start in activities:

        start_label = start.get_label()

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

            for nxt in graph[node]:

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
                    and nxt.get_label() == start_label
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
            list(visited_on_shortest) if best_distance is not None else None
        )

    return result