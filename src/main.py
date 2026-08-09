from pygments.lexers import asn1

from data_structures.activity import Activity
from data_structures.event import Event
from data_structures.log import Log
from data_structures.relations.transitive_reduced_strict_partial_order import TransitiveReducedStrictPartialOrder
from data_structures.trace import Trace
from src.log_creation.log_creator import get_log
from src.concurrency_miner import concurrency_miner

#TODO
# arbitrary order: muss zusätzlich noch gecheckt werden ob jede Partition mit jeder direct connected ist?
#                   bzw wenn sie keine start und end activity haben ,it arbitrary partition mergen

#TODO IMPORTANT FLOWER MODEL::: put every activity in a partition and create sublogs from that, so that all the traces are still there -> base cases / and loop will do the rest

#TODO Fallthroughs,
# done  Empty Log -> Tau
# done  Empty Trace -> x(Tau,...)
# done  activity once per trace -> if an acitivity is in every trace put it in concurrent and continue
#       concurrent activity -> put one activity in concurrent and see if a cut is found with the rest, if yes continue
#       strict tau loop ?
#       tau loop ?
# done  flower model -> return all activities concurrent and activities that occur more often (or not exactly once) in a tau loop ->for example concurrent(a, loop(tau, b), c)
#       if there is only one activity in the fall through dont return ^(a) -> instead return a or loop(tau, a) or x(tau,a) respectively

#TODO data handling
#       infrequent : wenn kein cuut gefunden wird edges zählen in den graphen -> directly follows, overlappping und ganz seltene entfernen (ganze Traces oder nur edges?)
#       incompleteness : Wenn kein cut gefunden wird edges in dfg und overlapping hinzufügen
#                       dafür werden wahrscheinlichkeiten für jede mögliche edge berechnet

#TODO Add good test cases (bigger constructs with all operators mixed)
#TODO correct and incorrect test cases
#TODO Tree to traces - parser -> Given a tree returns a Log with all possible Traces -> Good to create Testcases

#        case "exclusive":      # exclusive Log
#        case "sequence":       # sequence log
#        case "loop":           # loop log
#        case "sequence_loop":  # loop/sequence log
#        case "arbitrary":      # arbitrary order log
#        case "interleaving":   # interleafing log
#        case "concurrent":     # concurrent log
#        case "parallel":       # parallel log
#        case "x_parallel"      # exclusive/parallel log





a1 = Event(Activity("a"))
b1 = Event(Activity("b"))
c1 = Event(Activity("c"))
tspo5 = TransitiveReducedStrictPartialOrder(b1, c1)
tspo6 = TransitiveReducedStrictPartialOrder(a1, b1)
t1 = Trace([a1, b1, c1], [tspo5, tspo6])

a2 = Event(Activity("a"))
c2 = Event(Activity("c"))
tspo3 = TransitiveReducedStrictPartialOrder(c2, a2)
t2 = Trace([a2, c2], [tspo3])

b2 = Event(Activity("b"))
t3 = Trace([b2], [])

test_log = Log([t1, t2, t3])
print("-----------------------------------------------------------------------------------------------------------")
print(str(test_log))
print("-----------------------------------------------------------------------------------------------------------")
print(str(concurrency_miner(test_log)))
print("-----------------------------------------------------------------------------------------------------------")

