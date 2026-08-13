import copy
from itertools import combinations

def create_exclusive_choice_partitions(event_log):
    log = copy.deepcopy(event_log)

    # create partitions as lists with one trace each
    partitions = [[trace] for trace in log]

    for t1, t2 in combinations(log, 2):
        if len(partitions) < 2:
            break
        if not t1.get_activities().isdisjoint(t2.get_activities()):
            p1 = []
            p2 = []
            for p in partitions:
                if t1 in p:
                    p1 = p
                if t2 in p:
                    p2 = p
            if p1 != p2:
                partitions.remove(p1)
                partitions.remove(p2)
                p1.extend(p2)
                partitions.append(p1)
    return partitions