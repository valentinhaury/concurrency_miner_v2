from data_structures.relations.directly_follows_relation import DirectlyFollowsRelation
from src.data_structures.activity import Activity
from src.data_structures.trace import Trace
from src.data_structures.log import Log
from src.concurrency_miner import concurrency_miner


#TODO
# alle anpassen so wie im pseudocode zB.:
# exclusive choice so wie im Pseudocode umschreiben (combinations von traces und nicht von partitions)
# sequence detection so wie im Pseudocode umschreiben (combinations von activities nicht partitions -> ein loop)
# arbitrary order: muss zusätzlich noch gecheckt werden ob jede Partition mit jeder direct connected ist?
# algorithmus so anpassen, dass nicht true/false von detect returned wird, sondern dass im main algorithmus die länge geprüft wird -> spart zeit
# algorithmus so anpassen, dass dfg, efg, msd, ovl direkt übergeben werden und nur einmal am Anfang erstellt werden.
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

str_input = 'sequence_loop' # exclusive sequence arbitrary interleafing concurrent parallel loop sequence_loop
#test_log = get_log(str_input)
a1 = Activity("a")
a2 = Activity("a")
a3 = Activity("a")
b1 = Activity("b")
b2 = Activity("b")
b3 = Activity("b")
c1 = Activity("c")
c2 = Activity("c")
c3 = Activity("c")
d1 = Activity("d")
# a-c b-d a-d
t1 = Trace([a1, b1, c1, d1, a2],[DirectlyFollowsRelation(a2,a1), DirectlyFollowsRelation(a1, c1), DirectlyFollowsRelation(a1, d1), DirectlyFollowsRelation(b1, d1)])
test_log = Log([t1])

#get_log_without_activity
#detect_activity_once_per_trace
#get_activities_once_per_trace
print("-----------------------------------------------------------------------------------------------------------")

print("-----------------------------------------------------------------------------------------------------------")

print("-----------------------------------------------------------------------------------------------------------")
print("Discovered Tree")
process_tree = concurrency_miner(test_log)
print(str(process_tree))
print("-----------------------------------------------------------------------------------------------------------")
print("Input Log")
print(str(test_log))
print("-----------------------------------------------------------------------------------------------------------")