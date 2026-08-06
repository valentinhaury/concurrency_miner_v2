from src.data_structures.activity import Activity
from src.data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from src.data_structures.log import Log
from src.data_structures.trace import Trace

##
##
##
##
## USED FOR TESTING DONT CHANGE
def a():
    return Activity("a")
def b():
    return Activity("b")
def c():
    return Activity("c")
def d():
    return Activity("d")
def e():
    return Activity("e")
def f():
    return Activity("f")
def g():
    return Activity("g")
def h():
    return Activity("h")

def _arbitrary_trace_a_sequence():
    a1 = a()
    b1 = b()
    c1 = c()
    return Trace([a1, b1, c1], [DirectlyFollowsRelation(a1, b1), DirectlyFollowsRelation(b1, c1)])
def _arbitrary_trace_sequence_a():
    a1 = a()
    b1 = b()
    c1 = c()
    return Trace([a1, b1, c1], [DirectlyFollowsRelation(b1, c1), DirectlyFollowsRelation(c1, a1)])
def _interleafing_trace_a_sequence():
    a1 = a()
    b1 = b()
    c1 = c()
    return Trace([a1, b1, c1], [DirectlyFollowsRelation(b1, a1), DirectlyFollowsRelation(a1, c1)])
def _certain_parallel_trace_a_sequence():
    a1 = a()
    b1 = b()
    c1 = c()
    return Trace([a1, b1, c1], [DirectlyFollowsRelation(b1, c1)])


def get_log(specifier):
    match specifier:
        case "exclusive":       return _log_exclusive()          # exclusive Log
        case "sequence":        return _log_sequence()           # sequence log
        case "loop":            return _log_loop()               # loop log
        case "sequence_loop":   return _log_loop_sequence()      # loop log
        case "arbitrary":       return _log_arbitrary_order()    # arbitrary order log
        case "interleafing":    return _log_interleafing()       # interleafing log
        case "concurrent":      return _log_concurrent()         # concurrent log
        case "parallel":        return _log_parallel()           # parallel log
    return None


def _log_exclusive():
    a1 = a()
    b1 = b()
    trace_a = Trace([a1])
    trace_b = Trace([b1])
    return Log([trace_a, trace_b])

def _log_sequence():
    a1 = a()
    b1 = b()
    trace_a = Trace([a1, b1], [DirectlyFollowsRelation(a1, b1)])
    return Log([trace_a])

def _log_loop():
    a1 = a()
    a2 = a()
    b1 = b()
    trace_a = Trace([a1, a2, b1], [DirectlyFollowsRelation(a1, b1), DirectlyFollowsRelation(b1, a2)])
    return Log([trace_a])

def _log_loop_sequence():
    a1 = a()
    b1 = b()
    c1 = c()
    d1 = d()
    a2 = a()
    b2 = b()
    c2 = c()

    trace_a = Trace([a1, c1, a2, c2, b1, b2, d1], [DirectlyFollowsRelation(a1, b1), DirectlyFollowsRelation(b1, c1), DirectlyFollowsRelation(c1, d1), DirectlyFollowsRelation(d1, a2), DirectlyFollowsRelation(a2, b2), DirectlyFollowsRelation(b2, c2)])
    return Log([trace_a])

def _log_arbitrary_order():
    trace_a = _arbitrary_trace_a_sequence()
    trace_b = _arbitrary_trace_sequence_a()
    return Log([trace_a, trace_b])

def _log_interleafing():
    trace_a = _arbitrary_trace_a_sequence()
    trace_b = _arbitrary_trace_sequence_a()
    trace_c = _interleafing_trace_a_sequence()
    return Log([trace_a, trace_b, trace_c])

def _log_concurrent():
    trace_a = _arbitrary_trace_a_sequence()
    trace_b = _arbitrary_trace_sequence_a()
    trace_c = _interleafing_trace_a_sequence()
    a1 = a()
    b1 = b()
    c1 = c()
    trace_d = Trace([a1, b1, c1], [DirectlyFollowsRelation(a1, c1), DirectlyFollowsRelation(b1, c1)])
    a2 = a()
    b2 = b()
    c2 = c()
    trace_e = Trace([a2, b2, c2], [DirectlyFollowsRelation(b2, c2), DirectlyFollowsRelation(b2, a2)])
    trace_f = _certain_parallel_trace_a_sequence()
    return Log([trace_a, trace_b, trace_c, trace_d, trace_e, trace_f])

def _log_parallel():
    trace_f = _certain_parallel_trace_a_sequence()
    return Log([trace_f])