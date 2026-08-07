from src.log_creation.log_creator import get_log
from src.algorithm_components.split_detection.detect_parallel import detect_parallel, create_parallel_partitions
from src.data_structures.log import Log

def test_empty_log():

    log = Log([])

    activities = log.get_activities()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()

    parallel_partitions_of_empty_log = create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(parallel_partitions_of_empty_log) < 2

def test_exclusive_log():
    log = get_log("exclusive")

    activities = log.get_activities()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()

    parallel_partitions_of_exclusive_log = create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(parallel_partitions_of_exclusive_log) < 2

def test_sequence_log():
    log = get_log("sequence")

    activities = log.get_activities()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()

    parallel_partitions_of_sequence_log = create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(parallel_partitions_of_sequence_log) < 2

def test_arbitrary_order_log():
    log = get_log("arbitrary")

    activities = log.get_activities()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()

    parallel_partitions_of_arbitrary_log = create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(parallel_partitions_of_arbitrary_log) < 2

def test_interleaving_log():
    log = get_log("interleaving")

    activities = log.get_activities()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()

    parallel_partitions_of_interleaving_log = create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(parallel_partitions_of_interleaving_log) < 2

def test_concurrent_log():
    log = get_log("concurrent")

    activities = log.get_activities()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()

    parallel_partitions_of_concurrent_log = create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(parallel_partitions_of_concurrent_log) < 2

def test_parallel_log():
    log = get_log("parallel")

    activities = log.get_activities()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()

    parallel_partitions_of_parallel_log = create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(parallel_partitions_of_parallel_log) > 1

def test_loop_log():
    log = get_log("loop")

    activities = log.get_activities()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()

    parallel_partitions_of_loop_log = create_parallel_partitions(activities, overlapping_relations, eventually_follows_relations)

    assert len(parallel_partitions_of_loop_log) < 2