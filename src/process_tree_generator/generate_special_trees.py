from data_structures.process_tree import Node
from data_structures.process_tree_operator import Operator


def generate_tree_1():
    tree = Node(Operator.Arbitrary)
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

def generate_tree_3():
    tree = Node(Operator.Parallel)
    child1 = Node(Operator.Sequence)
    child2 = Node(Operator.Parallel)
    child1_1 = Node("A")
    child1_2 = Node("B")

    child1.add_child(child1_1)
    child1.add_child(child1_2)

    child2_1 = Node("C")
    child2_2 = Node("D")

    child2.add_child(child2_1)
    child2.add_child(child2_2)
    tree.add_child(child1)
    tree.add_child(child2)
    return tree

def generate_tree_4():
    tree = Node(Operator.Arbitrary)
    child1 = Node("A")
    child2 = Node("B")
    child3 = Node(Operator.Loop)
    child3_1 = Node("C")
    child3_2 = Node("D")
    child4 = Node("E")

    tree.add_child(child1)
    tree.add_child(child2)
    child3.add_child(child3_1)
    child3.add_child(child3_2)
    tree.add_child(child3)
    tree.add_child(child4)
    return tree