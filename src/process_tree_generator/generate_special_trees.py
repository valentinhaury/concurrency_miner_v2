from data_structures.process_tree import Node
from data_structures.process_tree_operator import Operator


def generate_tree_1():
    tree = Node(Operator.Parallel)
    child1 = Node("A")
    child2 = Node(Operator.Exclusive)

    child2_1 = Node(Operator.Multi)
    child2_1_1 = Node("B")

    child2_2 = Node("C")

    child2_1.add_child(child2_1_1)
    child2.add_child(child2_1)
    child2.add_child(child2_2)
    tree.add_child(child1)
    tree.add_child(child2)
    return tree

def generate_tree_2():
    tree = Node(Operator.Arbitrary)
    child1 = Node("A")
    child2 = Node(Operator.Concurrent)

    child2_1 = Node("B")

    child2_2 = Node("C")

    child2.add_child(child2_1)
    child2.add_child(child2_2)
    tree.add_child(child1)
    tree.add_child(child2)
    return tree