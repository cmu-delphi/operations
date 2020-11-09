"""Unit tests for utils.py."""

# standard library
import datetime
import unittest
from unittest.mock import MagicMock, sentinel

# py3tester coverage target
__test_target__ = 'delphi.operations.screenshots.utils'


class TimeUtilsTests(unittest.TestCase):

  def test_wait_for_condition_immediately_true(self):
    """Don't wait for a condition that's already met."""

    predicate = lambda: True
    timeout = datetime.timedelta(minutes=1)

    result = TimeUtils.wait_for_condition(
        predicate, timeout, time_impl=MagicMock())

    self.assertTrue(result)

  def test_wait_for_condition_before_timeout(self):
    """Wait for a condition without timing out."""

    predicate = MagicMock(side_effect=[False, True])
    timeout = datetime.timedelta(minutes=1)
    mock_time = MagicMock()
    mock_time.time.return_value = 123

    result = TimeUtils.wait_for_condition(
        predicate, timeout, time_impl=mock_time)

    self.assertTrue(result)

  def test_wait_for_condition_until_timeout(self):
    """Wait for a condition, exceeding the time limit."""

    predicate = lambda: False
    timeout = datetime.timedelta(minutes=1)
    mock_time = MagicMock()
    mock_time.time.side_effect = range(100)

    result = TimeUtils.wait_for_condition(
        predicate, timeout, time_impl=mock_time)

    self.assertFalse(result)


class DockerUtilsTests(unittest.TestCase):

  def test_build_image(self):
    """Build the screenshot image."""

    mock_docker_client = MagicMock()
    mock_docker_client.images.build.return_value = sentinel.image

    result = DockerUtils.build_image(mock_docker_client)

    self.assertEqual(result, sentinel.image)

  def test_run_container(self):
    """Start and stop a container."""

    screen_size = (123, 456)
    mock_container = MagicMock()
    mock_docker_client = MagicMock()
    mock_docker_client.containers.run.return_value = mock_container

    with DockerUtils.run_container(
        mock_docker_client, screen_size) as container:

      mock_docker_client.containers.run.assert_called_once()
      args, kwargs = mock_docker_client.containers.run.call_args
      env = kwargs['environment']
      self.assertEqual(env['SCREEN_WIDTH'], '123')
      self.assertEqual(env['SCREEN_HEIGHT'], '456')

      self.assertEqual(container, mock_container)
      mock_container.stop.assert_not_called()

    mock_container.stop.assert_called_once()

  def test_is_server_ready_not_ready(self):
    """Indicate that the server is not ready."""

    mock_container = MagicMock()
    mock_container.logs.return_value = b'foo'

    result = DockerUtils.is_server_ready(mock_container)

    self.assertFalse(result)

  def test_is_server_ready_ready(self):
    """Indicate that the server is ready."""

    mock_container = MagicMock()
    logs = b'foo' + DockerUtils.SELENIUM_READY_MESSAGE + b'bar'
    mock_container.logs.return_value = logs

    result = DockerUtils.is_server_ready(mock_container)

    self.assertTrue(result)

  def test_wait_for_server_without_timeout(self):
    """Block until the server is ready."""

    mock_time_utils = MagicMock()
    mock_time_utils.wait_for_condition.return_value = True

    DockerUtils.wait_for_server(MagicMock(), time_utils_impl=mock_time_utils)

    mock_time_utils.wait_for_condition.assert_called_once()

  def test_wait_for_server_with_timeout(self):
    """Raise when server is not ready by the timeout."""

    mock_time_utils = MagicMock()
    mock_time_utils.wait_for_condition.return_value = False

    with self.assertRaises(Exception):
      DockerUtils.wait_for_server(MagicMock(), time_utils_impl=mock_time_utils)

    mock_time_utils.wait_for_condition.assert_called_once()

  def test_get_host_port(self):
    """Inspect a running container to get the listening port."""

    mock_container = MagicMock()
    mock_container.ports = {
      DockerUtils.SELENIUM_HOST_PORT: [{'HostPort': sentinel.port}],
    }
    mock_docker_client = MagicMock()
    mock_docker_client.containers.get.return_value = mock_container

    result = DockerUtils.get_host_port(
        mock_docker_client, sentinel.container_id)

    mock_docker_client.containers.get.assert_called_once_with(
        sentinel.container_id)
    self.assertEqual(result, sentinel.port)


class TestSeleniumUtils(unittest.TestCase):

  def test_get_driver(self):
    """Connect and disconnect from a selenium server."""

    mock_driver = MagicMock()
    mock_webdriver = MagicMock()
    mock_webdriver.Remote.return_value = mock_driver

    with SeleniumUtils.get_driver(
        sentinel.port, webdriver_impl=mock_webdriver) as driver:

      mock_webdriver.Remote.assert_called_once()
      self.assertEqual(driver, mock_driver)
      mock_driver.close.assert_not_called()

    mock_driver.close.assert_called_once()


class TestUtils(unittest.TestCase):

  def test_run_screenshot_stack_goes_fullscreen(self):
    """After bringing up the stack, make the browser fullscreen."""

    with Utils.run_screenshot_stack(
        sentinel.screen_size,
        docker_impl=MagicMock(),
        docker_utils_impl=MagicMock(),
        selenium_utils_impl=MagicMock()) as driver:

      driver.fullscreen_window.assert_called_once()
