from itertools import product, combinations
from src.data_structures.relations.relation import Relation
from src.data_structures.relations.eventually_follows_relation import EventuallyFollowsRelation
from src.data_structures.relations.overlapping_relation import OverlappingRelation
from src.data_structures.relations.directly_follows_relation import TransitivReducedStrictPartialOrder


def fully_direct_connected(a1, a2, directly_follows_relations):
    if (TransitivReducedStrictPartialOrder(a1, a2).relation_exists_by_label(directly_follows_relations)
     and TransitivReducedStrictPartialOrder(a2, a1).relation_exists_by_label(directly_follows_relations)
     ):
        return True
    return False

def not_fully_direct_connected_relation(activities, directly_follows_relations):
    relations = []
    for a1, a2 in combinations(activities, 2):
        if not (TransitivReducedStrictPartialOrder(a1, a2).relation_exists_by_label(directly_follows_relations)
                and TransitivReducedStrictPartialOrder(a2, a1).relation_exists_by_label(directly_follows_relations)
        ):
           relations.append(Relation(a1, a2))
    return relations

def direct_connected_id(a1, a2, directly_follows_relations):
    if (TransitivReducedStrictPartialOrder(a1, a2).relation_exists_by_id(directly_follows_relations)
     or TransitivReducedStrictPartialOrder(a2, a1).relation_exists_by_id(directly_follows_relations)
     ):
        return True
    return False

def fully_eventually_connected_partitions(partition_1, partition_2, eventually_follows_relations):
    p1_follows_p2 = False
    p2_follows_p1 = False
    for a, b in product(partition_1, partition_2):
        if EventuallyFollowsRelation(a, b).relation_exists_by_label(eventually_follows_relations):
            p2_follows_p1 = True
        if EventuallyFollowsRelation(b, a).relation_exists_by_label(eventually_follows_relations):
            p1_follows_p2 = True
    return p1_follows_p2 and p2_follows_p1

def eventually_connected_in_only_one_direction_partitions(partition_1, partition_2, eventually_follows_relations):
    p1_follows_p2 = False
    p2_follows_p1 = False
    for a, b in product(partition_1, partition_2):
        if EventuallyFollowsRelation(a, b).relation_exists_by_label(eventually_follows_relations):
            p2_follows_p1 = True
        if EventuallyFollowsRelation(b, a).relation_exists_by_label(eventually_follows_relations):
            p1_follows_p2 = True
    return p1_follows_p2 != p2_follows_p1


def eventually_connected(a1, a2, eventually_follows_relations):
    if (EventuallyFollowsRelation(a1, a2).relation_exists_by_label(eventually_follows_relations)
            or EventuallyFollowsRelation(a2, a1).relation_exists_by_label(eventually_follows_relations)):
        return True
    return False

def overlapping(a1, a2, overlapping_relations):
    if (OverlappingRelation(a1, a2).relation_exists_by_label(overlapping_relations)
        or OverlappingRelation(a2, a1).relation_exists_by_label(overlapping_relations)):
        return True
    return False

def overlapping_partitions(partition_1, partition_2, overlapping_relations):
    for a, b in product(partition_1, partition_2):
        if OverlappingRelation(a, b).relation_exists_by_label(overlapping_relations) \
                or OverlappingRelation(b, a).relation_exists_by_label(overlapping_relations):
            return True
    return False

def fully_overlapping_partitions(partition_1, partition_2, overlapping_relations):
    for a, b in product(partition_1, partition_2):
        if not (OverlappingRelation(a, b).relation_exists_by_label(overlapping_relations)
                or OverlappingRelation(b, a).relation_exists_by_label(overlapping_relations)):
            return False
    return True

