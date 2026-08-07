from src.log_creation.log_creator import get_log
from src.algorithm_components.split_detection.detect_loop import detect_loop
from src.data_structures.log import Log

def test_empty_log():
    assert detect_loop(Log([])) == False

def test_exclusive_log():
    assert detect_loop(get_log("exclusive")) == False

def test_sequence_log():
    assert detect_loop(get_log("sequence")) == False

def test_arbitrary_order_log():
    assert detect_loop(get_log("arbitrary")) == False

def test_interleafing_log():
    assert detect_loop(get_log("interleaving")) == False

def test_concurrent_log():
    assert detect_loop(get_log("concurrent")) == False

def test_parallel_log():
    assert detect_loop(get_log("parallel")) == False

def test_loop_log():
    assert detect_loop(get_log("loop")) == True