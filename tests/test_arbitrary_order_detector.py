import copy

from src.algorithm_components.split_detection.detect_arbitrary_order import create_arbitrary_order_partitions
from src.log_creation.log_creator import get_log
from src.data_structures.log import Log

def _get_test_partitions(log):
    directly_follows_relations = log.get_directly_follows_relations()
    eventually_follows_relations = log.get_eventually_follows_relations()
    overlapping_relations = log.get_overlapping_relations()
    activities = log.get_activities()
    start_activities = log.get_start_activities()
    end_activities = log.get_end_activities()
    traces = log.get_traces()
    arbitrary_order_partitions = create_arbitrary_order_partitions(traces, activities, start_activities, end_activities, overlapping_relations,
                                                                         eventually_follows_relations,
                                                                         directly_follows_relations)
    return arbitrary_order_partitions

def test_empty_log():
    log = Log([])
    assert len(_get_test_partitions(log)) < 2

def test_exclusive_log():
    log = copy.deepcopy(get_log("exclusive"))
    assert len(_get_test_partitions(log)) < 2

def test_sequence_log():
    log = copy.deepcopy(get_log("sequence"))
    assert len(_get_test_partitions(log)) < 2

def test_arbitrary_order_log():
    log = copy.deepcopy(get_log("arbitrary"))
    assert len(_get_test_partitions(log)) > 1

def test_interleafing_log():
    log = copy.deepcopy(get_log("interleaving"))
    assert len(_get_test_partitions(log)) < 2

def test_concurrent_log():
    log = copy.deepcopy(get_log("concurrent"))
    assert len(_get_test_partitions(log)) < 2

def test_parallel_log():
    log = copy.deepcopy(get_log("parallel"))
    assert len(_get_test_partitions(log)) < 2

def test_loop_log():
    log = copy.deepcopy(get_log("loop"))
    assert len(_get_test_partitions(log)) < 2
