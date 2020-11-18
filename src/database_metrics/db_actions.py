"""Methods which send SQL queries to the MariaDB docker database."""
from docker.models.containers import Container, ExecResult


def _get_epidata_db_size(container: Container) -> ExecResult:
    """
    Query the size of the epidata database in megabytes.

    Parameters
    ----------
    container: Container
        Docker Container object where the MariaDB database is running.

    Returns
    -------
    ExecResult from exec_run, which will be the exit code and the query result as a bytestring.
    """
    db_sizes = container.exec_run(
        'mysql -uuser -ppass -e '
        '"SELECT table_schema db, sum(data_length + index_length)/1024/1024 size_mb '
        'FROM information_schema.TABLES GROUP BY table_schema ORDER BY table_schema;"')
    return db_sizes


def _get_covidcast_rows(container: Container) -> ExecResult:
    """
    Query the row count of the epidata.covidcast table.

    Parameters
    ----------
    container: Container
        Docker Container object where the MariaDB database is running.

    Returns
    -------
    ExecResult from exec_run, which will be the exit code and the query result as a bytestring.
    """
    row_count = container.exec_run(
        'mysql -uuser -ppass -e '
        '"SELECT count(*) FROM epidata.covidcast;"')
    return row_count


def _clear_cache(container: Container) -> ExecResult:
    """
    Clear MariaDB cache so query times can be measured independently.

    https://mariadb.com/kb/en/query-cache/#emptying-and-disabling-the-query-cache

    Parameters
    ----------
    container: Container
        Docker Container object where the MariaDB database is running.

    Returns
    -------
    ExecResult from exec_run, which will be the exit code and any output. No output means
    the command was successful.
    """
    return container.exec_run('mysql -uroot -ppass -e "FLUSH TABLES; RESET QUERY CACHE;"')


def _clear_db(container: Container) -> ExecResult:
    """
    Clear tables and cache so the covidcast tables and caches are reset.

    Runs _clear_cache() and then deletes rows from the covidcast data and metadata tables.

    Parameters
    ----------
    container: Container
        Docker Container object where the MariaDB database is running.

    Returns
    -------
    2-Tuple of ExecResults from exec_run, which will be the exit code and any output.
    No output means the command was successful. The first entry of the tuple is the ExecResult of
    _clear_cache() and the second entry will be the ExecResult from the table clearing query.
    """
    clear_tables = container.exec_run(
        'mysql -uroot -ppass -e '
        '"USE epidata; '
        'DELETE FROM covidcast; '
        'DELETE FROM covidcast_meta_cache;"')
    return _clear_cache(container), clear_tables
