# wenn in einem Trace eine start-activity auf eine end-activity folgt
# wird der Trace hier gesplittet, und der Log mit gesplitteten Traces wird
# zurückgegeben und dann durch Loop mit einem empty-log connected
import copy

from data_structures.trace import Trace


def create_strict_tau_loop_log(traces, start_activities, end_activities):
    old_traces = copy.deepcopy(traces)
    new_traces = []
    changed = True
    while old_traces and changed:
        old_trace = old_traces.pop()
        changed = False
        for relation in old_trace.get_transitive_reduced_strict_partial_order():
            if relation.get_first().get_activity() in end_activities and relation.get_second.get_activity() in start_activities:
                