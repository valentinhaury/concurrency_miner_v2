from log_creation.create_variants_from_event_log import get_variants_from_event_log
from src.log_creation.create_traces_from_variants import create_traces_from_variants
from pm4py.objects.log.importer.xes import importer as xes_importer


import_log = xes_importer.apply("test_data/test_input_arbitrary.xes")
variants = get_variants_from_event_log(import_log)
event_log = create_traces_from_variants(variants)