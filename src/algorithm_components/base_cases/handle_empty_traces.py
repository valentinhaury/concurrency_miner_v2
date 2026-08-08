import copy

from src.data_structures.event import Event
from src.data_structures.log import Log
from src.data_structures.trace import Trace
from src.data_structures.activity import Activity

def handle_empty_traces(log):
    log_traces = copy.deepcopy(log.get_log_traces())
    new_log_traces = []

    for trace in log_traces:
        if trace.get_events():
            new_log_traces.append(trace)
        else:
            new_log_traces.append(Trace(Event(Activity("tau")), set()))
    # return a new log with all events from the old log and Event with "tau" activity for the empty traces
    log = Log(new_log_traces)
    return log

