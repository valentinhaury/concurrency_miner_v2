from src.data_structures.activity import Activity

def detect_single_activity(traces):
    for trace in traces:
        if len(trace.get_events()) > 1:
            return False
    return True

def get_single_activity(log):
    activities = log.get_activities_by_label()
    if activities:
        return activities[0]
    else:
        return Activity("tau")
