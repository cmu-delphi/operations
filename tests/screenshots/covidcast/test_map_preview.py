"""Unit tests for map_preview.py."""

# standard library
import argparse
from contextlib import ExitStack
import unittest
from unittest.mock import MagicMock, patch, sentinel

# py3tester coverage target
__test_target__ = 'delphi.operations.screenshots.covidcast.map_preview'


class MapPreviewTests(unittest.TestCase):

  def test_get_most_recent_date_success(self):
    """Get the most recent date for a signal."""

    mock_epidata = MagicMock()
    mock_epidata.covidcast.return_value = {
      'result': 1,
      'epidata': [{'time_value': 2}, {'time_value': 3}, {'time_value': 1}]
    }

    date = MapPreview.get_most_recent_date(
        None, None, None, None, epidata_impl=mock_epidata)

    self.assertEqual(date, '3')

  def test_get_most_recent_date_fail(self):
    """Fail to get timing for a nonexistent signal."""

    mock_epidata = MagicMock()
    mock_epidata.covidcast.return_value = {'result': -2}

    with self.assertRaises(MapPreviewException):
      MapPreview.get_most_recent_date(
          None, None, None, None, epidata_impl=mock_epidata)

  def test_take_screenshot_saves_screenshot(self):
    """Run through the screenshot flow."""

    mock_map = MagicMock()
    mock_map.find_elements_by_class_name.return_value = [mock_map] * 10
    mock_driver = MagicMock()
    mock_driver.title = 'COVIDcast'
    mock_driver.find_elements_by_css_selector.return_value = [mock_map]
    mock_args = MagicMock()
    mock_args.path = sentinel.path

    MapPreview.take_screenshot(
        mock_driver,
        mock_args,
        sentinel.date,
        time_impl=MagicMock(),
        webdriver_impl=MagicMock())

    # there are many calls, but this is the last and most important
    mock_map.screenshot.assert_called_once_with(sentinel.path)

  def test_take_screenshot_checks_page_title(self):
    """Don't take a screenshot when the page title is unexpected."""

    mock_driver = MagicMock()
    mock_driver.title = 'foo'

    with self.assertRaises(MapPreviewException):
      MapPreview.take_screenshot(
          mock_driver,
          MagicMock(),
          None,
          time_impl=MagicMock(),
          webdriver_impl=MagicMock())

  def test_take_screenshot_shows_failure_reason(self):
    """Re-wrap screenshot exceptions with a hint of what caused the failure."""

    mock_driver = MagicMock()
    mock_driver.title = 'COVIDcast'
    mock_driver.find_elements_by_css_selector.return_value = []

    with self.assertRaises(MapPreviewException):
      MapPreview.take_screenshot(
          mock_driver,
          MagicMock(),
          None,
          time_impl=MagicMock(),
          webdriver_impl=MagicMock())

  def test_get_argument_parser(self):
    """Return an ArgumentParser."""

    result = MapPreview.get_argument_parser()
    self.assertIsInstance(result, argparse.ArgumentParser)

  def test_main_with_date(self):
    """Launch the main entry point with a specific date."""

    mock_context = MagicMock()
    mock_context.__enter__.return_value = sentinel.driver
    mock_utils = MagicMock()
    mock_utils.run_screenshot_stack.return_value = mock_context
    mock_args = MagicMock()
    mock_args.date = sentinel.date
    mock_args.width = 123
    mock_args.height = 456

    with patch.object(MapPreview, 'take_screenshot') as mock_take_screenshot:
      MapPreview.main(mock_args, utils_impl=mock_utils)
      mock_take_screenshot.assert_called_once_with(
          sentinel.driver, mock_args, sentinel.date)

    mock_utils.run_screenshot_stack.assert_called_once_with(
        (123, 456 + 311))

  def test_main_without_date(self):
    """Launch the main entry point without specifying a date."""

    mock_context = MagicMock()
    mock_context.__enter__.return_value = sentinel.driver
    mock_utils = MagicMock()
    mock_utils.run_screenshot_stack.return_value = mock_context
    mock_args = MagicMock()
    mock_args.date = None
    mock_args.source = sentinel.source
    mock_args.signal = sentinel.signal
    mock_args.geo_type = sentinel.geo_type
    mock_args.geo_value = sentinel.geo_value
    mock_args.width = 123
    mock_args.height = 456

    with ExitStack() as stack:
      mock_get_most_recent_date = stack.enter_context(
          patch.object(MapPreview, 'get_most_recent_date'))
      mock_get_most_recent_date.return_value = sentinel.date
      mock_take_screenshot = stack.enter_context(
          patch.object(MapPreview, 'take_screenshot'))

      MapPreview.main(mock_args, utils_impl=mock_utils)

      mock_get_most_recent_date.assert_called_once_with(
          sentinel.source,
          sentinel.signal,
          sentinel.geo_type,
          sentinel.geo_value)
      mock_take_screenshot.assert_called_once_with(
          sentinel.driver, mock_args, sentinel.date)

    mock_utils.run_screenshot_stack.assert_called_once_with(
        (123, 456 + 311))
