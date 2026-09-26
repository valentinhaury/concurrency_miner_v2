import string

from data_structures.trace import Trace
from developement_utilities.process_tree_generator.process_tree_generator import generate_process_tree
from developement_utilities.process_tree_generator.simple_trace_to_trace import get_trace_from_simple_trace
from developement_utilities.process_tree_generator.process_tree_to_traces import generate_traces


def generate_scalable_event_log(num_activities, num_events, num_traces):
    activities = list(string.ascii_uppercase[:num_activities])
    correct_length_traces = []
    counter = 0
    allowed_deviation = (num_events + 9) // 10 + 1

    while len(correct_length_traces) < 2:
        counter += 1
        correct_length_traces = []

        tree = generate_process_tree(activities)
        log_from_tree = generate_traces(tree)

        for simple_trace in log_from_tree:
            trace = get_trace_from_simple_trace(simple_trace)
            if num_events - allowed_deviation < len(trace.get_events()):
                correct_length_traces.append(trace)

        if counter == 1000:
            raise RuntimeError(
                f"can't find traces with length {num_events}"
            )
        print(counter)

    traces = []
    print("number of variants: ", len(correct_length_traces))
    while len(traces) < num_traces:
        for trace in correct_length_traces:
            traces.append(trace)

            if len(traces) == num_traces:
                break

    return traces