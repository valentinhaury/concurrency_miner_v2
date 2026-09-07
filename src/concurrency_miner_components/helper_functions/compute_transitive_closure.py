import copy
from itertools import permutations


def compute_transitive_closure(relation):
    relation = copy.deepcopy(relation)
    changed = True
    while changed:
        changed = False
        for r1, r2 in permutations(relation, 2):
            if r1[1] == r2[0]:
                if (r1[0], r2[1]) not in relation:
                    relation.add((r1[0], r2[1]))
                    changed = True
    return relation