import multiprocessing as mp
import time
from functools import partial
from typing import Callable

from docker.models.containers import Container
from docker import DockerClient
from delphi.operations.database_metrics.db_actions import _get_epidata_db_size, \
    _get_covidcast_rows, \
    _clear_db
from delphi.operations.database_metrics.actions import load_data, update_meta, send_query
from delphi.operations.database_metrics.parsers import parse_metrics


def measure_database(datasets: list,
                     client: DockerClient,
                     db_container: Container,
                     image: str = "delphi-python",
                     queries: list = None,
                     append_datasets: bool = False) -> dict:
    """
    Measure performance metrics for a list of functions and datasets.

    For each dataset in `datasets`, measure load time, metadata update time, and optional queries.
    Datasets are specified by a tuple of (source, file_pattern).
    e.g. ("usa-facts", "202003*_county*"), which will load all the county level usa-facts data
    for March 2020.

    Parameters
    ----------
    datasets: list of tuples
        List of 2-tuples defined as (source, patterns for files) to be included in each dataset.
    client: DockerClient
        DockerClient object to access and execute python images.
    db_container: str
        Name of Docker container containing the database to measure.
    image: str, optional
        Name of Docker image containing the data loading and metadata updating code. Defaults to 'delphi-python'.
    queries: list of dictionaries, optional
        List of query parameters to test query runtimes on. Defaults to empty list.
    append_datasets: boolean, optional
        Boolean for whether to append each dataset onto the previous one (True), or clear the
        database for each dataset (False). Defaults to False.

    Returns
    -------
    Dictionary of metrics. Keys will be the datasets and values will be dicts containing the output
    of parse_metrics() for loading, metadata updates, and queries.
    """
    db = client.containers.get(db_container)
    output = {"load": [], "meta": [], "datasets": datasets, "append_datasets": append_datasets, "queries": queries}
    query_funcs = [partial(send_query, params=p) for p in queries] if queries is not None else []
    meta_func = partial(update_meta, client=client, image=image)
    for dataset in datasets:
        if not append_datasets:
            _clear_db(db)
        load_func = partial(load_data, client=client, image=image, source=dataset[0], file_pattern=dataset[1])
        output["load"].append(parse_metrics(get_metrics(load_func, db)))
        output["meta"].append(parse_metrics(get_metrics(meta_func, db)))
        for i, query in enumerate(query_funcs):
            output[f"query{i}"] = output.get(f"query{i}", []) + [parse_metrics(get_metrics(query, db_container))]
    return output


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
    return (_get_covidcast_rows(container).output,
            _get_epidata_db_size(container).output,
            end_time-start_time,
            container_stats)
