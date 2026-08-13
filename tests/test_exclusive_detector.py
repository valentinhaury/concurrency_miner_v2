from src.log_creation.log_creator import get_log
from src.algorithm_components.partitioning.detect_exclusive import create_exclusive_choice_partitions
from src.data_structures.log import Log

def test_empty_log():
    assert len(create_exclusive_choice_partitions(Log([]))) < 2

def test_exclusive_log():
    assert len(create_exclusive_choice_partitions(get_log("exclusive"))) > 1

def test_sequence_log():
    assert len(create_exclusive_choice_partitions(get_log("sequence"))) < 2

def test_arbitrary_order_log():
    assert len(create_exclusive_choice_partitions(get_log("arbitrary"))) < 2

def test_interleafing_log():
    assert len(create_exclusive_choice_partitions(get_log("interleaving"))) < 2

def test_concurrent_log():
    assert len(create_exclusive_choice_partitions(get_log("concurrent"))) < 2

def test_parallel_log():
    assert len(create_exclusive_choice_partitions(get_log("parallel"))) < 2

def test_loop_log():
    assert len(create_exclusive_choice_partitions(get_log("loop"))) < 2