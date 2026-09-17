from evaluation_tools.trace_tree_matcher import TraceTreeMatcher


def get_fitness_score(event_log, process_tree):
    fitness = 0
    for trace in event_log:
        trace_matcher = TraceTreeMatcher(trace)
        if trace_matcher.trace_fits_tree(process_tree):
            fitness += 1
    return fitness / len(event_log)

