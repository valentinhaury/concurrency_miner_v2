

from data_structures.process_tree import Node
from data_structures.process_tree_operator import Operator
from process_tree_generator.generate_special_trees import generate_tree_1, generate_tree_2, generate_tree_3
from process_tree_generator.process_tree_generator import generate_process_tree
from process_tree_generator.process_tree_to_traces import generate_traces
from process_tree_generator.simple_trace_to_trace import get_trace_from_simple_trace
from src.log_creation.create_event_log_from_xes import create_event_log_from_data_input_xes

from src.concurrency_miner import concurrency_miner

#TODO Add good test cases (bigger constructs with all operators mixed)
# correct and incorrect test cases
# #1 generate a random process tree and generate traces from that tree randomly -> use as input
# #2 add noise to traces: select a specific number i.e. 10% of traces randomly and change them by adding an activity, changing an activity name or change the order of two activities
# #3 generate a large event log with
#       1. average trace length
#       2. number of traces
#       3. number of activities

#TODO
# arbitrary order: muss zusätzlich noch gecheckt werden ob jede Partition mit jeder direct connected ist?
#                   bzw wenn sie keine start und end activity haben mit arbitrary partition mergen

#TODO data handling
#       infrequent : wenn kein cut gefunden wird edges zählen in den graphen -> directly follows, overlappping und ganz seltene entfernen (ganze Traces oder nur edges?)
#                       -> in wie vielen Traces kommen sie vor, zählen pro event geht nicht
#       incompleteness : Wenn kein cut gefunden wird edges in dfg und overlapping hinzufügen
#                       dafür werden wahrscheinlichkeiten für jede mögliche edge berechnet


if False:
    activities = {
        "A",
        "B",
        "C",
        "D",
    }
# Generate a random tree with the activities
    tree = generate_process_tree(activities)

#TODO IMPORTANT Irgendwann wurden Arbitrary und Concurrent vertauscht?? sicher?
#               -> Arbitrary mit interleaving vertauscht in generate_tree_2
#               , aber das ist schon richtig so -> Problem mit Language Uniqueness? -> funktioniert es wenn das arbitrary zuerst kommt?


tree = generate_tree_1()


print(tree)
tree.print_tree()
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

event_log = []
for simple_trace in generate_traces(tree):
    #print("simple: " + str(simple_trace))
    trace = get_trace_from_simple_trace(simple_trace)
    event_log.append(trace)
    print(trace.get_strict_partial_order())
    print("ovl" + str(trace.get_overlapping_events()))

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
new_tree = concurrency_miner(event_log)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

print(str(new_tree))
new_tree.print_tree()




if False:
    test_log = create_event_log_from_data_input_xes()

    print("-----------------------------------------------------------------------------------------------------------")
    tree = concurrency_miner(test_log)
    print(str(tree))
    print("-----------------------------------------------------------------------------------------------------------")
    tree.print_tree()
