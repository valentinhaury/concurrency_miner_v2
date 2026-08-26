from pygments.lexers import asn1

from process_tree_generator.process_tree_generator import generate_process_tree
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
#                   bzw wenn sie keine start und end activity haben ,it arbitrary partition mergen

#TODO data handling
#       infrequent : wenn kein cut gefunden wird edges zählen in den graphen -> directly follows, overlappping und ganz seltene entfernen (ganze Traces oder nur edges?)
#                       -> in wie vielen Traces kommen sie vor, zählen pro event geht nicht
#       incompleteness : Wenn kein cut gefunden wird edges in dfg und overlapping hinzufügen
#                       dafür werden wahrscheinlichkeiten für jede mögliche edge berechnet

#TODO Tree to traces - parser -> Given a tree returns a Log with all possible Traces

activities = {
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J"
}

tree = generate_process_tree(activities)

print(tree)
print()

tree.print_tree()


if False:
    test_log = create_event_log_from_data_input_xes()

    print("-----------------------------------------------------------------------------------------------------------")
    tree = concurrency_miner(test_log)
    print(str(tree))
    print("-----------------------------------------------------------------------------------------------------------")
    tree.print_tree()
