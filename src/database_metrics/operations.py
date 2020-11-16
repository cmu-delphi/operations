"""Operations for which metrics are captured for."""
import requests
from requests import Response

from docker import DockerClient


def send_query(params: dict) -> Response:
    """
    Send query to Epidata API running on docker MariaDB container.

    Parameters
    ----------
    params: dict
        Query parameters to send. List of parameters can be found here:
        https://cmu-delphi.github.io/delphi-epidata/api/covidcast.html#constructing-api-queries

    Returns
    -------
    Requests Response object.
    """
    req = requests.get("http://localhost:10080/epidata/api.php",
                       params=params)
    return req


def load_data(client: DockerClient, source: str, file_pattern: str) -> bytes:
    """
    Ingest data into epidata database using the Python docker image.

    Copies files from common_full/covidcast/receiving/`source`/`file_pattern`, which should be
    copied to the image via the DockerFile, to the common/covidcast/receiving/`source`/ folder
    for ingestion. Runs ingestion via the python command.

    Parameters
    ----------
    client: DockerClient
        Docker Client object containing the Python image.
    source: str
        Data source name
    file_pattern: str
        Filename of pattern to match

    Returns
    -------
    Bytestring of Docker log, either STDOUT or STDERR
    """
    return client.containers.run(
        image=client.images.get("delphi_python"),
        command=f'bash -c "mkdir -p /common/covidcast/receiving/usa-facts && \
        cp common_full/covidcast/receiving/{source}/{file_pattern} '
                f'/common/covidcast/receiving/{source}/ && \
        python3 -m delphi.epidata.acquisition.covidcast.csv_to_database '
                f'--data_dir /common/covidcast/"',
        network="delphi-net")


def update_meta(client: DockerClient) -> bytes:
    """
    Update metadata cache in database.

    Parameters
    ----------
    client: DockerClient
        Docker Client object containing the Python image.

    Returns
    -------
    Bytestring of Docker log, either STDOUT or STDERR
    """
    return client.containers.run(
        image=client.images.get("delphi_python"),
        command="python3 -m delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater",
        network="delphi-net")
