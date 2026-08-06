import copy

def get_loop_activities(event_log):
    log = copy.deepcopy(event_log)
    activities = []
    candidates = log.get_activities_by_label()
    for candidate in candidates:
        looping = False
        for trace in log.get_traces():
            count = 0
            for activity in trace.get_activities():
                if activity.get_label() == candidate.get_label():
                    count += 1
            if count > 1:
                looping = True
                break
        if looping:
            activities.append(candidate)
    return activities