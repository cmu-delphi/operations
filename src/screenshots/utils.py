"""Contains functionally required by most screenshot drivers.

Functionallity includes:
- docker commands for starting the `delphi_screenshot` server
- initialization of the selenium webdriver
- graceful setup and teardown
"""

# standard library
from contextlib import contextmanager
import datetime

# first party
import time

# third party
import docker
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TimeUtils:

  def wait_for_condition(predicate, timeout, time_impl=time):
    """
    Block until a condition is met or until a timeout has elapsed, whichever
    happens first.

    Parameters
    ----------
    predicate : function
        A function which takes no arguments and returns a bool indicating
        whether the condition has been met.
    timeout : datetime.timedelta
        The maximum amount of time to wait before returning. Note that the
        condition is checked once per second, so timeouts are effectively
        lower-bounded by one second.
    """

    is_condition_met = predicate()
    end_time = time_impl.time() + timeout.total_seconds()
    while not is_condition_met and time_impl.time() < end_time:
      time_impl.sleep(1)
      is_condition_met = predicate()
    return is_condition_met


class DockerUtils:

  # the name (or tag, in docker terms) of the screenshot image
  IMAGE_NAME = 'delphi_screenshot'

  # a relative path to the build context and Dockerfile
  BUILD_CONTEXT_PATH = 'delphi/operations/screenshots/docker'

  # the port on which the upstream selenium image listens
  SELENIUM_HOST_PORT = '4444/tcp'

  # the magic log string which indicates that the selenium server is ready
  SELENIUM_READY_MESSAGE = b'Selenium Server is up and running'

  def build_image(docker_client):
    """Build the screenshot image.

    Parameters
    ----------
    docker_client : docker.DockerClient
        A client for communicating with a Docker server.

    Returns
    -------
    docker.models.images.Image
        A handle to the image that was built.
    """

    print(f'building {DockerUtils.IMAGE_NAME}')
    return docker_client.images.build(
        path=DockerUtils.BUILD_CONTEXT_PATH,
        tag=DockerUtils.IMAGE_NAME,
        forcerm=True)

  @contextmanager
  def run_container(docker_client, screen_size):
    """Run the screenshot container.

    A direct call yields a single container instance. However, this function is
    meant to be called indirectly as a context manager, in which case the
    container is provided through a `with` statement.

    To prevent blocking, the container is started in the background, in
    detached mode. It must be explicitly stopped, otherwise it would run
    forever. The context manager stops the container when the `with` block
    exits.

    To avoid accumulation of stopped containers, the `auto_remove` option is
    enabled, which causes the docker engine to delete the container upon exit.

    Parameters
    ----------
    docker_client : docker.DockerClient
        A client for communicating with a Docker server.
    screen_size : (int, int)
        The width and height in pixels of the virtual screen.

    Yields
    -------
    docker.models.containers.Container
        A handle to the container that was started.
    """

    print(f'running {DockerUtils.IMAGE_NAME}')
    container = docker_client.containers.run(
        DockerUtils.IMAGE_NAME,
        # delete the container after it exists
        auto_remove=True,
        # start the container in the background
        detach=True,
        # pass the given screen dimensions
        environment={
          'SCREEN_WIDTH': f'{screen_size[0]}',
          'SCREEN_HEIGHT': f'{screen_size[1]}',
        },
        # forward an ephemeral port on localhost to the contained server
        ports={
          DockerUtils.SELENIUM_HOST_PORT: ('127.0.0.1', None),
        },
        # the selenium chrome container requires much more than the default
        # amount of shared memory; see
        # https://github.com/SeleniumHQ/docker-selenium/blob/trunk/README.md#quick-start
        shm_size='2g')

    try:
      yield container
    finally:
      container.stop()
      print('container stopped')

  def is_server_ready(container):
    """Return whether the selenium server is ready to accept connections.

    Parameters
    ----------
    container : docker.models.containers.Container
        A container running a selenium server.

    Returns
    -------
    bool
        Whether the selenium server is ready to accept connections.
    """

    return DockerUtils.SELENIUM_READY_MESSAGE in container.logs(tail=1)

  def wait_for_server(container, time_utils_impl=TimeUtils):
    """Wait for the selenium server to become ready.

    Parameters
    ----------
    container : docker.models.containers.Container
        A container running a selenium server.

    Raises
    ------
    Exception
        If the server isn't ready after 10 seconds.
    """

    print('waiting for server to initialize')
    predicate = lambda: DockerUtils.is_server_ready(container)
    timeout = datetime.timedelta(seconds=10)
    if not time_utils_impl.wait_for_condition(predicate, timeout):
      raise Exception('timeout waiting for server to initialize')

  def get_host_port(docker_client, container_id):
    """Get the TCP port number which is forwarded to the container.

    Parameters
    ----------
    docker_client : docker.DockerClient
        A client for communicating with a Docker server.
    container_id : str
        The ID of the container to inspect.

    Returns
    -------
    int
        The TCP port number which is forwarded to the container.
    """

    container = docker_client.containers.get(container_id)
    return container.ports[DockerUtils.SELENIUM_HOST_PORT][0]['HostPort']


class SeleniumUtils:

  @contextmanager
  def get_driver(port, webdriver_impl=webdriver):
    """Create a webdriver for a Chrome instance in a local selenium container.

    A direct call yields a single driver instance. However, this function is
    meant to be called indirectly as a context manager, in which case the
    driver is provided through a `with` statement.

    It's best practice to close the driver when finished, which is done
    automatically in this case by using a context manager.

    Parameters
    ----------
    port : int
        The local TCP port on which the selenium server is listening.

    Yields
    -------
    selenium.webdriver.remote.webdriver
        A remote webdriver instance connected to a local selenium container.
    """

    print('connecting to chrome')
    driver = webdriver_impl.Remote(
        command_executor=f'http://127.0.0.1:{port}/wd/hub',
        desired_capabilities=DesiredCapabilities.CHROME)

    try:
      yield driver
    finally:
      driver.close()
      print('driver closed')


class Utils:

  @contextmanager
  def run_screenshot_stack(
      screen_size,
      docker_impl=docker,
      docker_utils_impl=DockerUtils,
      selenium_utils_impl=SeleniumUtils):
    """Start the screenshot stack and return a live webdriver.

    A direct call yields a single driver instance. However, this function is
    meant to be called indirectly as a context manager, in which case the
    driver is provided through a `with` statement.

    All resource initialization and cleanup is handled though context managers.

    Parameters
    ----------
    screen_size : (int, int)
        The width and height in pixels of the virtual screen.

    Yields
    -------
    selenium.webdriver.remote.webdriver
        A remote webdriver instance connected to a local selenium container.
    """

    docker_client = docker_impl.from_env()
    docker_utils_impl.build_image(docker_client)

    with docker_utils_impl.run_container(
        docker_client, screen_size) as container:

      docker_utils_impl.wait_for_server(container)
      # get the port only after the server is ready
      port = docker_utils_impl.get_host_port(docker_client, container.id)

      with selenium_utils_impl.get_driver(port) as driver:

        # make the virtual browser window fullscreen in the virtual display
        driver.fullscreen_window()
        yield driver
