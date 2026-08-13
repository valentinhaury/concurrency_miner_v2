from src.algorithm_components.helper_functions.sublog_functions import create_sublogs_loop

def create_flower_model_partitions(activities):
    partitions = []
    for activity in activities:
        partitions.append({activity})
    return partitions

def get_flower_model_sublogs(log, partitions):
    return create_sublogs_loop(log, partitions)