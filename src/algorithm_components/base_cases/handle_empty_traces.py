from src.data_structures.activity import Activity

def handle_empty_traces(log):
    for trace in log.get_traces():
        if not trace.get_events():
            trace.add_activity(Activity("tau"))
