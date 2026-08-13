from copy import copy

from pm4py.objects.log.obj import EventLog, Trace

from pm4py.objects.log.util.interval_lifecycle import to_interval
from pm4py.util.xes_constants import (
    DEFAULT_NAME_KEY,
    DEFAULT_START_TIMESTAMP_KEY,
    DEFAULT_TIMESTAMP_KEY,
    DEFAULT_TRANSITION_KEY,
)

from cortado_core.utils.cvariants import create_graphs, unique_activities, create_variants
from cortado_core.utils.timestamp_utils import TimeUnit

def get_variants_from_event_log(
    log: EventLog,
    use_mp: bool = False,
    time_granularity: TimeUnit = min(TimeUnit),
    pool=None,
):
    if log.attributes.get("PM4PY_TYPE", "") != "interval":
        if DEFAULT_TRANSITION_KEY in log[0][0]:
            traces = [
                Trace(
                    [
                        e
                        for e in trace
                        if e[DEFAULT_TRANSITION_KEY].lower() == "start"
                        or e[DEFAULT_TRANSITION_KEY].lower() == "complete"
                    ],
                    attributes=trace.attributes,
                    properties=trace.properties,
                )
                for trace in log
            ]
            log = EventLog(
                traces,
                attributes=copy(log.attributes),
                extensions=log.extensions,
                classifiers=log.classifiers,
                omni_present=log.omni_present,
                properties=log.properties,
            )

    interval_log = to_interval(log)
    interval_log_filtered = EventLog(
        [trace for trace in interval_log if len(trace) > 0],
        attributes=copy(log.attributes),
        extensions=log.extensions,
        classifiers=log.classifiers,
        omni_present=log.omni_present,
        properties=log.properties,
    )

    log_renamed, names = unique_activities(interval_log_filtered)
    graphs = create_graphs(
        log_renamed, interval_log_filtered, use_mp, time_granularity, pool
    )

    id_name_map = {name: id for id, name in enumerate(names.keys())}

    variants = create_variants(graphs, names, id_name_map, use_mp, pool)

    return variants