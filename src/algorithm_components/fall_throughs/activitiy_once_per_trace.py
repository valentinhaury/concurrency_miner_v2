import copy


def detect_activity_once_per_trace(event_log):
    log = copy.deepcopy(event_log)
    if get_activities_once_per_trace(log):
        return True
    else:
        return False

def get_activities_once_per_trace(traces):
    activities_in_every_trace = set()
    activities_in_every_trace |= traces[0].get_activities()
    for trace in traces:
        activities_in_every_trace &= trace.get_activities()

    return activities_in_every_trace