from datetime import datetime

from log_creation.create_variants_from_event_log import get_variants_from_event_log
from src.log_creation.create_traces_from_variants import create_traces_from_variants
from pm4py.objects.log.importer.xes import importer as xes_importer


def create_event_log_from_data_input_xes(
):
    log = xes_importer.apply("data/BPI_Challenge_2012.xes")
    print(f"[{datetime.now():%H:%M:%S}] Log imported")
    variants = get_variants_from_event_log(log)
    print(f"[{datetime.now():%H:%M:%S}] Variants created")
    traces = create_traces_from_variants(variants)
    print(f"[{datetime.now():%H:%M:%S}] Traces Created from Variants")
    return traces