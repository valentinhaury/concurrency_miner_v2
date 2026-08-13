import copy

from src.log_creation.log_creator import get_log
from src.algorithm_components.partitioning.detect_sequence import create_sequence_partitions
from src.data_structures.log import Log

def test_empty_log():

    log = Log([])
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    sequence_partitions_of_empty_log = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(sequence_partitions_of_empty_log) < 2

def test_exclusive_log():

    log = copy.deepcopy(get_log("exclusive"))
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    sequence_partitions_of_exclusive_log = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(sequence_partitions_of_exclusive_log) < 2

def test_sequence_log():

    log = copy.deepcopy(get_log("sequence"))
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    sequence_partitions_of_sequence_log = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(sequence_partitions_of_sequence_log) > 1

def test_arbitrary_order_log():
    log = copy.deepcopy(get_log("arbitrary"))
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    sequence_partitions_of_arbitrary_log = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(sequence_partitions_of_arbitrary_log) < 2

def test_interleafing_log():
    log = copy.deepcopy(get_log("interleaving"))
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    sequence_partitions_of_interleafing_log = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(sequence_partitions_of_interleafing_log) < 2

def test_concurrent_log():
    log = copy.deepcopy(get_log("concurrent"))
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    sequence_partitions_of_concurrent_log = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(sequence_partitions_of_concurrent_log) < 2

def test_parallel_log():
    log = copy.deepcopy(get_log("parallel"))
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    sequence_partitions_of_parallel_log = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(sequence_partitions_of_parallel_log) < 2

def test_loop_log():
    log = copy.deepcopy(get_log("loop"))
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    sequence_partitions_of_loop_log = create_sequence_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(sequence_partitions_of_loop_log) < 2
