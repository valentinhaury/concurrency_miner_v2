
from developement_utilities.log_creation.create_event_log_from_xes import create_event_log_from_data_input_xes
from developement_utilities.process_tree_generator.generate_special_trees import generate_tree_2
from developement_utilities.process_tree_generator.process_tree_generator import generate_process_tree
from developement_utilities.process_tree_generator.process_tree_to_traces import generate_traces
from developement_utilities.process_tree_generator.simple_trace_to_trace import get_trace_from_simple_trace
from evaluation_tools.trace_tree_precision import EscapingEdgesPrecision
from evaluation_tools.tree_fitness import get_fitness_score

from src.concurrency_miner import concurrency_miner

#TODO Add good test cases (bigger constructs with all operators mixed)
# correct and incorrect test cases
# DONE  #1 generate a random process tree and generate traces from that tree randomly -> use as input
#       #2 add noise to traces: select a specific number i.e. 10% of traces randomly and change them by adding an activity, changing an activity name or change the order of two activities
#       #3 generate a large event log with
#           1. average trace length
#           2. number of traces
#           3. number of activities

#TODO
# arbitrary order: -> merge with an always direct connected partition -> if this fails just ignore it or merge it to arbitrary -> merging with arbitrary will lead to less likely finding a split

#todo
# CONCURRENT ->  overlapping AND directly-complete     //     overlapping OR directly-complete

#TODO empty traces vor oder nach dem split finding ersetzen?

#TODO
# Fallthroughs concurrent or interleaving depending if that activity is overlapping with any other activity


activities = {
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
}
# Generate a random tree with given activities
#tree = generate_process_tree(activities)

# Generate specified tree
tree = generate_tree_2()


# Print tree input
print(tree)
tree.print_tree()
tree = generate_tree_2()
log_from_tree = []
for simple_trace in generate_traces(tree):
    trace = get_trace_from_simple_trace(simple_trace)
    log_from_tree.append(trace)
    print(str(trace))



print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
new_tree = concurrency_miner(log_from_tree)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print(str(new_tree))
new_tree.print_tree()
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
fitness_score = get_fitness_score(log_from_tree, new_tree)
print("FITNESS SCORE: " + str(fitness_score))

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

evaluator = EscapingEdgesPrecision(
    log=log_from_tree,
    process_tree=tree,
)

precision = evaluator.precision()

print("Precision:", precision)



if False:
    log_from_xes = create_event_log_from_data_input_xes()

    #0.01; 0.02; 0.03; 0.04;
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    new_tree = concurrency_miner(log_from_xes)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print(str(new_tree))
    new_tree.print_tree()

