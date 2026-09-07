from data_structures.trace import Trace
from src.concurrency_miner_components.helper_functions.partition_functions import merge_partitions

def create_filtered_sublogs_sequential(log, partitions):
    sublogs = []
    for _ in partitions:
        sub_log = []
        sublogs.append(sub_log)

    for old_trace in log:
        old_trace_partitions = []
        for event in old_trace.get_events():
            old_trace_partitions.append([event])
        for (a, b) in old_trace.get_overlapping_events():
            merge_partitions(a, b, old_trace_partitions)

        old_strict_partial_order = old_trace.get_strict_partial_order()
        # sort partitions
        n = len(old_trace_partitions)
        for i in range(n):
            a = next(iter(old_trace_partitions[i]))
            for j in range(i + 1, n):
                b = next(iter(old_trace_partitions[j]))
                if (a, b) not in old_strict_partial_order:
                    old_trace_partitions[i], old_trace_partitions[j] = old_trace_partitions[j], old_trace_partitions[i]

        partitions_assignments = best_assignment(old_trace_partitions, partitions)
        for partition_index, assignment in enumerate(partitions_assignments):
            new_trace_events = set()
            for event_partition in assignment:
                new_trace_events |= {event for event in event_partition if event.get_label() in partitions[partition_index]}

            #TODO implement get_new_trace_from_events_and_old_trace(new_trace_events, old_trace) and use everything below

            # new strict partial order is old strict partial order
            new_trace_strict_partial_order = {
                relation
                for relation in old_trace.get_strict_partial_order()
                if set(relation).issubset(new_trace_events)
            }

            # new transitive reduced strict partial order is the transitive reduction of the new strict partial order
            new_trace_transitive_reduced_strict_partial_order = set(new_trace_strict_partial_order)
            for r in new_trace_strict_partial_order:
                for e in new_trace_events:
                    if (r[0], e) in new_trace_strict_partial_order and (e, r[1]) in new_trace_strict_partial_order:
                        new_trace_transitive_reduced_strict_partial_order.discard(r)

            # new overlapping relation is old overlapping relation
            new_trace_overlapping_relations = {
                relation
                for relation in old_trace.overlapping_relations
                if set(relation).issubset(new_trace_events)
            }
            new_trace = Trace(
                new_trace_events,
                new_trace_transitive_reduced_strict_partial_order,
                new_trace_strict_partial_order,
                new_trace_overlapping_relations
            )
            #TODO Everything until here
            sublogs[partition_index].append(
                new_trace
            )

    return sublogs

def best_assignment(event_partitions, activity_partitions):
    n = len(event_partitions)
    m = len(activity_partitions)

    # cost of an event_partition if assigned to a specific activity_partition
    def cost(event_partition, activity_partition):
        return sum(event.get_label() not in activity_partition for event in event_partition)

    costs = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(cost(event_partitions[i], activity_partitions[j]))
        costs.append(row)

    # dp[i][j]:
    # minimale Kosten für die ersten i Eventpartitionen
    # und die ersten j Aktivitätspartitionen
    dp = [[float("inf")] * (m + 1) for _ in range(n + 1)]

    # parent[i][j] speichert, wie viele Eventpartitionen
    # der j-ten Aktivität zugeordnet wurden
    parent = [[None] * (m + 1) for _ in range(n + 1)]

    # Keine Events -> beliebig viele leere Aktivitäten
    for j in range(m + 1):
        dp[0][j] = 0

    for j in range(1, m + 1):
        for i in range(n + 1):

            # k = Anzahl der Eventpartitionen,
            # die Aktivität j-1 bekommt
            for k in range(i + 1):

                start = i - k

                current_cost = sum(
                    costs[x][j - 1]
                    for x in range(start, i)
                )

                candidate = dp[start][j - 1] + current_cost

                if candidate < dp[i][j]:
                    dp[i][j] = candidate
                    parent[i][j] = k

    # Zuordnung rekonstruieren
    assignment = [[] for _ in range(m)]

    i = n
    j = m

    while j > 0:
        k = parent[i][j]

        start = i - k

        assignment[j - 1] = list(range(start, i))

        i = start
        j -= 1

    return assignment