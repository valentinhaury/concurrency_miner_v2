from pygments.lexers import asn1

from src.log_creation.create_event_log_from_xes import create_event_log_from_data_input_xes

from src.concurrency_miner import concurrency_miner

#TODO Add good test cases (bigger constructs with all operators mixed)
# correct and incorrect test cases

#TODO
# arbitrary order: muss zusätzlich noch gecheckt werden ob jede Partition mit jeder direct connected ist?
#                   bzw wenn sie keine start und end activity haben ,it arbitrary partition mergen

#TODO data handling
#       infrequent : wenn kein cut gefunden wird edges zählen in den graphen -> directly follows, overlappping und ganz seltene entfernen (ganze Traces oder nur edges?)
#                       -> in wie vielen Traces kommen sie vor, zählen pro event geht nicht
#       incompleteness : Wenn kein cut gefunden wird edges in dfg und overlapping hinzufügen
#                       dafür werden wahrscheinlichkeiten für jede mögliche edge berechnet

#TODO Tree to traces - parser -> Given a tree returns a Log with all possible Traces


test_log = create_event_log_from_data_input_xes()

print("-----------------------------------------------------------------------------------------------------------")
tree = concurrency_miner(test_log)
print(str(tree))
print("-----------------------------------------------------------------------------------------------------------")
tree.print_tree()
