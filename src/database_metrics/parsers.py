"""Parse database and container metrics into more usable formats."""


def parse_db_size(query_result: bytes) -> float:
    r"""
    Parse the output of the SQL query in _get_epidata_db_size() to return the epidata database size.

    The _get_epidata_db_size() ExecResult output will be a bytestring like
    `b'db\tsize_mb\nepidata\t7.79687500\ninformation_schema\t0.18750000\n'`. This function
    will parse out the first value which should correspond to the epidata db.

    Parameters
    ----------
    query_result: bytes
        Bytestring result from _get_epidata_db_size().

    Returns
    -------
    Float representing size of epidata database in megabytes.
    """
    db_disks = query_result.decode().split("\n")
    epidata_usage = db_disks[1].split("\t")[1]
    return float(epidata_usage)


def parse_row_count(query_result: bytes) -> int:
    r"""
    Parse the output of the SQL query in _get_covidcast_rows() to return the covidcast row count.

    The _get_covidcast_rows() ExecResult output will be a bytestring like
    b'count(*)\n1604\n'. This function will retrieve 1604 as an integer

    Parameters
    ----------
    query_result: bytes
        Bytestring result from _get_epidata_db_size().

    Returns
    -------
    Float representing size of epidata database in megabytes.
    """
    db_rows = query_result.decode().split("\n")[1]
    return int(db_rows)


def parse_metrics(metrics: tuple) -> dict:
    """
    Parse and convert the metrics captured by get_metrics() into a dictionary.

    The main role of this is to parse the enormous dict returned by docker.container.stats and just
    retrieve the memory usage as a list. NOTE: memory_usage_mb is total usage in megabytes,
    while the `docker stats` command line command reports total - cache.

    Parameters
    ----------
    metrics: tuple
        3-Tuple of metrics output by get_metrics().

    Returns
    -------
    Dictionary containing final disk usage, runtime, and list of memory usage during function call.
    """
    output = {"table_rows": parse_row_count(metrics[0]),
              "db_disk_usage_mb": parse_db_size(metrics[1]),
              "runtime": metrics[2],
              "memory_usage_mb": max(i["memory_stats"]["usage"] / 1024 / 1024 for i in metrics[3])}
    return output
