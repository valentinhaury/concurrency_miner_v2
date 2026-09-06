from data_structures.event import Event
from data_structures.process_tree import Node
from data_structures.trace import Trace


def infrequent_concurrency_miner(
        event_log: list[Trace],
        filter_threshold: int,
):
    # handle empty log
    if not event_log:
        return Node("tau")

    # handle empty traces
    number_of_empty_traces = 0
    for trace in event_log:
        if len(trace.get_events()) == 0:
            number_of_empty_traces += 1

    log = []
    #TODO maybe this should already be at threshold / 10 ?? 
    if number_of_empty_traces / len(event_log) >= filter_threshold:
        log = [Trace({Event("tau")}, set(), set(), set()) if len(old_trace.get_events()) == 0 else old_trace for old_trace in event_log]
    else:
        for trace in event_log:
            if len(trace.get_events()) > 0:
                log.append(trace)


    return False