import time

from src.concurrency_miner import concurrency_miner, logger
from src.developement_utilities.logger import performance_logger
from src.scalability_evaluation.generate_scalable_log import generate_scalable_event_log


#def evaluate_concurrency_miner(num_activities, num_traces, num_events):
num_activities = 10
num_events = 20
num_traces = 100

for _ in range(10):

    print("generating traces...")
    event_log = generate_scalable_event_log(num_activities, num_events, num_traces)
    print("traces generated")
    logger.info("start concurrency miner")

    start = time.perf_counter()

    result = concurrency_miner(event_log)

    runtime = time.perf_counter() - start

    logger.info("end concurrency miner")
    logger.info(str(result))
    performance_logger.info(
        "activities=%d traces=%d events_per_trace=%d runtime=%.6f",
        num_activities,
        num_traces,
        num_events,
        runtime
    )