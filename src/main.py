import copy


from developement_utilities.log_creation.create_event_log_from_xes import get_2017_full_event_log
from developement_utilities.process_tree_generator.generate_special_trees import generate_tree_example_1
from developement_utilities.process_tree_generator.process_tree_generator import generate_process_tree
from developement_utilities.process_tree_generator.process_tree_to_traces import generate_traces
from developement_utilities.process_tree_generator.simple_trace_to_trace import get_trace_from_simple_trace

from src.concurrency_miner import concurrency_miner

from src.developement_utilities.logger import get_logger

logger = get_logger(__name__)


if False:
    activities = {
        "A",
        "B",
        "C",
        "D",
        "E"
    }
    # Generate a random tree with given activities
    tree = generate_process_tree(activities)

    # Generate specified tree
    tree = generate_tree_example_1()

    # Print tree input
    print(tree)
    tree.print_tree()
    log_from_tree = []
    for simple_trace in generate_traces(tree):
        trace = get_trace_from_simple_trace(simple_trace)
        log_from_tree.append(trace)
        print(str(trace))

    print("Number of traces: ", len(log_from_tree))

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    new_tree = concurrency_miner(copy.deepcopy(log_from_tree))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(str(new_tree))
    new_tree.print_tree()

    new_model = new_tree
    event_log = log_from_tree

#get_2012_full_event_log()
#get_2012_w_event_log()
#get_2017_full_event_log()
#get_2017_w_event_log()

    log_from_xes = get_2017_full_event_log()

    # W2017 0.1 threshold finds a loop ### W2012 0.2 ###
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    new_tree = concurrency_miner(copy.deepcopy(log_from_xes), 0.3)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print(str(new_tree))
    new_tree.print_tree()

    logger.info("TREE: " + str(new_tree))
