import copy

from src.log_creation.log_creator import get_log
from src.algorithm_components.partitioning.loop_partitioning import create_loop_partitions
from src.data_structures.log import Log

def test_empty_log():

    log = Log([])

    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    directly_follows_relations = log.get_directly_follows_relations()

    loop_partitions_of_empty_log = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)

    assert len(loop_partitions_of_empty_log) < 2

def test_exclusive_log():

    log = copy.deepcopy(get_log("exclusive"))

    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    directly_follows_relations = log.get_directly_follows_relations()

    loop_partitions_of_exclusive_log = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)

    assert len(loop_partitions_of_exclusive_log) < 2

def test_sequence_log():

    log = copy.deepcopy(get_log("sequence"))

    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    directly_follows_relations = log.get_directly_follows_relations()

    loop_partitions_of_sequence_log = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)

    assert len(loop_partitions_of_sequence_log) < 2

def test_arbitrary_order_log():
    log = copy.deepcopy(get_log("arbitrary"))

    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    directly_follows_relations = log.get_directly_follows_relations()

    loop_partitions_of_arbitrary_log = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)

    assert len(loop_partitions_of_arbitrary_log) < 2

def test_interleafing_log():
    log = copy.deepcopy(get_log("interleaving"))

    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    directly_follows_relations = log.get_directly_follows_relations()

    loop_partitions_of_interleafing_log = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)

    assert len(loop_partitions_of_interleafing_log) < 2

def test_concurrent_log():
    log = copy.deepcopy(get_log("concurrent"))

    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    directly_follows_relations = log.get_directly_follows_relations()

    loop_partitions_of_concurrent_log = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)

    assert len(loop_partitions_of_concurrent_log) < 2

def test_parallel_log():
    log = copy.deepcopy(get_log("parallel"))

    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    directly_follows_relations = log.get_directly_follows_relations()

    loop_partitions_of_parallel_log = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)

    assert len(loop_partitions_of_parallel_log) < 2

def test_loop_log():
    log = copy.deepcopy(get_log("loop"))

    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    overlapping_relations = log.get_overlapping_relations()
    directly_follows_relations = log.get_directly_follows_relations()

    loop_partitions_of_loop_log = create_loop_partitions(activities, start_activities, end_activities, overlapping_relations, directly_follows_relations)

    assert len(loop_partitions_of_loop_log) > 1