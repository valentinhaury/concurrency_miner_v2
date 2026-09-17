import copy

from src.data_structures.process_tree import Node
from src.data_structures.process_tree_operator import Operator
from src.data_structures.trace import Trace
from src.data_structures.event import Event
from developement_utilities.log_creation.create_event_log_from_xes import create_event_log_from_data_input_xes
from developement_utilities.process_tree_generator.generate_special_trees import generate_tree_2, generate_tree_3, \
    generate_tree_1, generate_test_tree_test_log_for_precision, generate_tree_4
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
# arbitrary order with 2 activity children will be directly connected to every other activity but shouldn't be separated

#TODO empty traces vor oder nach dem split finding ersetzen?

#TODO
# Fallthroughs concurrent or interleaving depending if that activity is overlapping with any other activity
if False:
    print(type(node.value) is Operator)
    print(type(node.value).__module__)
    print(Operator.__module__)
    print(type(node.value).__qualname__)
    print(Operator.__qualname__)

#if False:
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
#tree = generate_tree_4()

# Print tree input
print(tree)
tree.print_tree()
log_from_tree = []
for simple_trace in generate_traces(tree):
    trace = get_trace_from_simple_trace(simple_trace)
    log_from_tree.append(trace)
    #print(str(trace))

print("Number of traces: ", len(log_from_tree))

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
new_tree = concurrency_miner(copy.deepcopy(log_from_tree))
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print(str(new_tree))
new_tree.print_tree()

new_model = new_tree
event_log = log_from_tree

if False:
    log_from_xes = create_event_log_from_data_input_xes()

    #0.01; 0.02; 0.03; 0.04;
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    new_tree = concurrency_miner(copy.deepcopy(log_from_xes))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print(str(new_tree))
    new_tree.print_tree()

    new_model = new_tree
    event_log = log_from_xes


#event_log, new_model = generate_test_tree_test_log_for_precision()

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
fitness_score = get_fitness_score(event_log, new_model)
print("FITNESS SCORE: " + str(fitness_score))

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

evaluator = EscapingEdgesPrecision(
    log=event_log,
    process_tree=new_model,
)

precision = evaluator.precision()

print("Precision:", precision)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")