import copy
from itertools import combinations, permutations

from src.data_structures.relations.strict_partial_order import StrictPartialOrder
from src.data_structures.relations.transitive_reduced_strict_partial_order import TransitiveReducedStrictPartialOrder
from src.data_structures.log import Log
from src.data_structures.trace import Trace

def get_log_without_activity(event_log, activity):
    log = copy.deepcopy(event_log)
    activity_label = activity.get_label()
    new_log = Log()
    for trace in log.get_traces():
        new_trace = Trace()
        #add all activities that have a different label then the removed activity
        for a1 in trace.get_activities():
            if a1.get_label() != activity_label:
                new_trace.add_activity(a1)
        #add all relations between the other activities
        for relation in trace.get_directly_follows_relations():
            if relation.get_first_activity().get_label() != activity_label and relation.get_second_activity().get_label() != activity_label:
                new_trace.add_directly_follows_relation(relation)
        #add relations, so that activities are connected that were previously connected through the removed activity
        for r1, r2 in combinations(trace.get_directly_follows_relations(), 2):
            if r1.get_second_activity().get_label() == activity_label and r1.get_second_activity() == r2.get_first_activity():
                new_trace.add_directly_follows_relation(TransitiveReducedStrictPartialOrder(r1.get_first_activity(), r2.get_second_activity()))
        new_log.add_trace(new_trace)
    return new_log

def create_sublogs_concurrent(log, partitions):
    sublogs = []
    for partition in partitions:
        sub_log = []
        for trace in log.get_traces():

            new_trace_events = set()
            new_trace_transitive_reduced_strict_partial_order = set()

            events = trace.get_events()
            strict_partial_order = trace.get_strict_partial_order()
            transitive_reduced_strict_partial_order = trace.get_transitive_reduced_strict_partial_order()

            for event in events:
                if event.get_activity() in partition:
                    new_trace_events.add(event)

            for relation in transitive_reduced_strict_partial_order:
                if relation.get_first() in new_trace_events and relation.get_second() in new_trace_events:
                    new_trace_transitive_reduced_strict_partial_order.add(relation)

            for e1, e2 in permutations(new_trace_events, 2):
                if not StrictPartialOrder(e1, e2) in strict_partial_order:
                    continue
                connected = True
                for e3 in new_trace_events:
                    if StrictPartialOrder(e1, e3) in strict_partial_order and StrictPartialOrder(e3, e2)in strict_partial_order:
                        connected = False
                        break
                if connected:
                    new_trace_transitive_reduced_strict_partial_order.add(TransitiveReducedStrictPartialOrder(e1, e2))

            sub_log.append(Trace(new_trace_events, new_trace_transitive_reduced_strict_partial_order))
        sublogs.append(Log(sub_log))

    return sublogs


def create_sublogs_sequential(log, partitions):
    sublogs = []
    for partition in partitions:
        sub_log = []
        for trace in log.get_traces():
            new_trace_events = set()
            new_trace_transitive_reduced_strict_partial_order = set()
            for event in trace.get_events():
                if event.get_activity() in partition:
                    new_trace_events.add(event)
            for relation in trace.get_transitive_reduced_strict_partial_order():
                if relation.get_first() in new_trace_events and relation.get_second() in new_trace_events:
                    new_trace_transitive_reduced_strict_partial_order.add(relation)
            sub_log.append(Trace(new_trace_events, new_trace_transitive_reduced_strict_partial_order))
        sublogs.append(Log(sub_log))

    return sublogs
