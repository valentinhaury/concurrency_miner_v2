from itertools import combinations
from src.data_structures.relations.strict_partial_order import StrictPartialOrder

def detect_multi_instance(traces):
   for trace in traces:
        for e1, e2 in combinations(trace.get_events(), 2):
            if StrictPartialOrder(e1, e2) in trace.get_strict_partial_order() or StrictPartialOrder(e2, e1) in trace.get_strict_partial_order():
                return False
   return True