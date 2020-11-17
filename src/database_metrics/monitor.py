import multiprocessing as mp
import time
from typing import Callable

from docker.models.containers import Container
from .db_actions import _get_epidata_db_size


def get_metrics(func: Callable, container: Container) -> tuple:
    """
    Get runtime, disk usage, and memory usage for a container during a function call.

    The runtime may be up to 1s higher than the actual time since container.stats()
    takes a second to return. This also means if the function finishes in under 1s, it will
    still report a runtime of 1s.

    This polling behavior is also the reason for the use of `else: break` in the for loop instead of
    `while worker_process.is_alive()`, since keeping the same container.stats generator instead of
    calling it each loop lets us capture more data points.


    Parameters
    ----------
    func: Callable
        Function to run while metrics are captured.
    container: Container
        Docker Container object which will be monitored.

    Returns
    -------
    3-Tuple of final disk usage, runtime, and list of dicts containing docker stats.
    """
    worker_process = mp.Process(target=func)
    container_stats = [container.stats(stream=False)]  # get one stat right before starting process
    start_time = time.time()
    worker_process.start()
    for stat in container.stats(decode=True):
        if worker_process.is_alive():
            container_stats.append(stat)
        else:
            break
    end_time = time.time()
    return _get_epidata_db_size(container), end_time-start_time, container_stats
