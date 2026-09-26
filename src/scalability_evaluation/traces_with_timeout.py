import multiprocessing

from developement_utilities.process_tree_generator.process_tree_to_traces import generate_traces


def _generate_traces_worker(tree):
    return list(generate_traces(tree))


def generate_traces_with_timeout(tree, timeout=120):
    with multiprocessing.Pool(1) as pool:
        result = pool.apply_async(_generate_traces_worker, (tree,))

        try:
            return result.get(timeout=timeout)
        except multiprocessing.TimeoutError:
            pool.terminate()
            pool.join()
            return None