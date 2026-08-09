import copy
from itertools import combinations

from src.data_structures.trace import Trace
from src.data_structures.log import Log
from src.data_structures.relations.strict_partial_order import StrictPartialOrder

def detect_single_activity(traces):
    for trace in traces:
        if len(trace.get_events()) > 1:
            return False
    return True

def detect_multi_instance(traces):
   for trace in traces:
        for e1, e2 in combinations(trace.get_events(), 2):
            if StrictPartialOrder(e1, e2) in trace.get_strict_partial_order() or StrictPartialOrder(e2, e1) in trace.get_strict_partial_order():
                return False
   return True

def detect_single_loop(traces):
    for trace in traces:
        for e1, e2 in combinations(trace.get_events(), 2):
            if StrictPartialOrder(e1, e2) in trace.get_strict_partial_order() or StrictPartialOrder(e2, e1) in trace.get_strict_partial_order():
                return True
    return False

def create_single_loop_sublog(log):
    sublog = Log()
    for trace in log.get_traces():
        events = copy.deepcopy(trace.get_events())
        while events:
            new_trace_events = set()
            event = events.pop()
            new_trace_events.add(event)

            for e2 in events:
                if not StrictPartialOrder(event, e2) in trace.get_strict_partial_order() and not StrictPartialOrder(e2, event) in trace.get_strict_partial_order():
                    new_trace_events.add(e2)

            events -= new_trace_events
            sublog.add_trace(Trace(new_trace_events, set()))
    return [sublog, Log([])]


