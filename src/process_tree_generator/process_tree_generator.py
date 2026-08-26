import random

from data_structures.process_tree import Node
from data_structures.process_tree_operator import Operator

def generate_process_tree(activities):

    activities = list(activities)
    random.shuffle(activities)
    return _generate_subtree(activities)


def _generate_subtree(activities):
    n = len(activities)

    #base case -> returns a single activity or wrapped in multi instance
    if n == 1:
        activity = activities[0]
        if random.random() < 0.15:
            node = Node(Operator.Multi)
            node.add_child(Node(activity))
            return node
        return Node(activity)

    #choose a random operator
    operator = _choose_operator()

    #handle parallel differently
    if operator == Operator.Parallel:
        return _generate_parallel(activities)


    return _generate_normal_operator(
        operator,
        activities
    )


def _choose_operator():

    operators = [
        Operator.Exclusive,
        Operator.Sequence,
        Operator.Arbitrary,
        Operator.Interleaving,
        Operator.Concurrent,
        Operator.Parallel,
        Operator.Loop,
    ]

    weights = [
        0.18,  # Exclusive
        0.20,  # Sequence
        0.10,  # Arbitrary
        0.12,  # Interleaving
        0.12,  # Concurrent
        0.10,  # Parallel
        0.08,  # Loop
    ]

    return random.choices(
        operators,
        weights=weights,
        k=1
    )[0]



def _generate_normal_operator(operator, activities):
    n = len(activities)
    number_of_children = random.randint(
        2,
        min(4, n)
    )

    partitions = _random_partition(
        activities,
        number_of_children
    )

    node = Node(operator)

    for partition in partitions:
        child = _generate_subtree(partition)
        node.add_child(child)

    return node



def _generate_parallel(activities):

    n = len(activities)

    number_of_children = random.randint(
        2,
        min(3, n)
    )

    partitions = _random_partition(
        activities,
        number_of_children
    )

    node = Node(Operator.Parallel)

    # only one child (and their descendants) of the parallel operator is allowed to have sequences etc. as operators
    complex_child_index = random.randrange(
        number_of_children
    )

    for i, partition in enumerate(partitions):

        if i == complex_child_index and len(partition) > 1:
            child = _generate_subtree(partition)

        else:
            if len(partition) == 1:
                child = Node(partition[0])

            else:
                child = Node(Operator.Exclusive)

                for activity in partition:
                    child.add_child(
                        Node(activity)
                    )

        node.add_child(child)

    return node


def _random_partition(activities, number_of_children):

    activities = list(activities)
    random.shuffle(activities)

    #every partition contains at least one activity
    partitions = [
        [activities[i]]
        for i in range(number_of_children)
    ]

    # add the remaining activities
    for item in activities[number_of_children:]:
        random.choice(partitions).append(item)

    return partitions