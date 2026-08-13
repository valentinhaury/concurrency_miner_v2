# It's not possible to implement this with partial orders
import copy

def create_strict_tau_loop_log(traces, start_activities, end_activities):
    old_traces = copy.deepcopy(traces)
    new_traces = []
    changed = True
    while old_traces and changed:
        old_trace = old_traces.pop()
        changed = False
        for relation in old_trace.get_transitive_reduced_strict_partial_order():
            if relation.get_first().get_label() in end_activities and relation.get_second.get_label() in start_activities:
                print("Impossible")