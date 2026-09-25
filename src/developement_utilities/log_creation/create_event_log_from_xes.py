from datetime import datetime

from developement_utilities.log_creation.create_variants_from_event_log import get_variants_from_event_log
from developement_utilities.log_creation.create_traces_from_variants import create_traces_from_variants
from pm4py.objects.log.importer.xes import importer as xes_importer

from src.developement_utilities.logger import get_logger

logger = get_logger(__name__)

def get_2012_full_event_log():
    log = xes_importer.apply("developement_utilities/data/bpi_challenges/BPI_Challenge_2012.xes")
    logger.info("***Log imported***")
    logger.info("BPI_Challenge_2012")
    return create_event_log_from_data_input_xes(log)

def get_2012_w_event_log():
    log = xes_importer.apply("developement_utilities/data/bpi_challenges/BPI2012_W_START_COMPLETE.xes")
    logger.info("***Log imported***")
    logger.info("BPI2012_W_START_COMPLETE")
    return create_event_log_from_data_input_xes(log)

def get_2017_full_event_log():
    log = xes_importer.apply("developement_utilities/data/bpi_challenges/BPI_Challenge_2017.xes")
    logger.info("***Log imported***")
    logger.info("BPI_Challenge_2017")
    return create_event_log_from_data_input_xes(log)

def get_2017_w_event_log():
    log = xes_importer.apply("developement_utilities/data/bpi_challenges/BPI2017_W_START_COMPLETE.xes")
    logger.info("***Log imported***")
    logger.info("BPI2017_W_START_COMPLETE")
    return create_event_log_from_data_input_xes(log)


def create_event_log_from_data_input_xes(log):

    variants = get_variants_from_event_log(log)
    logger.info("***Variants created***")
    traces = create_traces_from_variants(variants)
    logger.info("***Traces Created from Variants***")
    return traces