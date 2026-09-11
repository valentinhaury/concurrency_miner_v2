from src.data_structures.process_tree import Node
from src.data_structures.process_tree_operator import Operator

def get_single_activity_node(single_activity, log_overlapping_relation, log_directly_follows):
    if not log_overlapping_relation and not log_directly_follows:
        process_tree = Node(single_activity)
        return process_tree
    single_activity_pair = (single_activity, single_activity)
    if single_activity_pair in log_overlapping_relation and single_activity_pair not in log_directly_follows:
        process_tree = (Node(Operator.Multi))
        process_tree.add_child(Node(single_activity))
        return process_tree
    if single_activity_pair not in log_overlapping_relation and single_activity_pair in log_directly_follows:
        process_tree = Node(Operator.Loop)
        process_tree.add_child(Node(single_activity))
        process_tree.add_child(Node("tau"))
        return process_tree
    else:
        multi_node = Node(Operator.Multi)
        multi_node.add_child(Node(single_activity))
        process_tree = Node(Operator.Loop)
        process_tree.add_child(multi_node)
        process_tree.add_child(Node("tau"))
        return process_tree