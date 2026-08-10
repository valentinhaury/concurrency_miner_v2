from pm4py.objects.log.importer.xes import importer as xes_importer
from cortado_core.utils.cgroups_graph import cgroups_graph


# --------------------------------------------------
# 1. XES-Datei importieren
# --------------------------------------------------

log = xes_importer.apply("../data/BPI_Challenge_2012.xes")

print("Anzahl Traces:", len(log))


# --------------------------------------------------
# 2. Einen Trace auswählen
# --------------------------------------------------

trace = log[0]

print("Anzahl XES-Events:", len(trace))


# --------------------------------------------------
# 3. START- und COMPLETE-Events zusammenführen
# --------------------------------------------------

events = []

# Offene START-Events speichern
open_events = {}

for event in trace:

    name = event["concept:name"]
    lifecycle = event["lifecycle:transition"]
    timestamp = event["time:timestamp"]

    if lifecycle == "START":
        open_events[name] = timestamp

    elif lifecycle == "COMPLETE":

        # Gibt es einen vorherigen START?
        if name in open_events:

            start_timestamp = open_events.pop(name)

            events.append({
                "concept:name": name,
                "start_timestamp": start_timestamp,
                "time:timestamp": timestamp,
            })

        else:
            # COMPLETE ohne START
            events.append({
                "concept:name": name,
                "start_timestamp": timestamp,
                "time:timestamp": timestamp,
            })


# --------------------------------------------------
# 4. Nach Startzeit sortieren
# --------------------------------------------------

events.sort(key=lambda x: x["start_timestamp"])


# --------------------------------------------------
# 5. C-Groups berechnen
# --------------------------------------------------

group = cgroups_graph(events, "seconds")


# --------------------------------------------------
# 6. Ergebnisse ausgeben
# --------------------------------------------------

print("\nEvents:")
print(group.events)

print("\nParallel:")
print(group.concurrency_pairs)

print("\nFollows:")
print(group.follows)

print("\nDirectly follows:")
print(group.directly_follows)

print("\nStart:")
print(group.start_activities)

print("\nEnd:")
print(group.end_activities)