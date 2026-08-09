from src.algorithm_components.helper_functions.sublog_functions import get_loop_sublogs

def create_flower_model_partitions(activities):
    partitions = []
    for activity in activities:
        partitions.append({activity})
    return partitions

def get_flower_model_sublogs(log, partitions):
    return get_loop_sublogs(log, partitions)