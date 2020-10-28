"""Unit tests for map_preview.py."""

# standard library
import argparse
import unittest
from unittest.mock import MagicMock, patch, sentinel

# py3tester coverage target
__test_target__ = 'delphi.operations.screenshots.covidcast.map_preview'


class MapPreviewTests(unittest.TestCase):

  def test_take_screenshot(self):
    """Run through the screenshot flow."""

    mock_map = MagicMock()
    mock_driver = MagicMock()
    mock_driver.title = 'COVIDcast'
    mock_driver.find_elements_by_css_selector.return_value = [mock_map]

    MapPreview.take_screenshot(
        mock_driver,
        sentinel.path,
        time_impl=MagicMock(),
        webdriver_impl=MagicMock())

    # there are many calls, but this is the last and most important
    mock_map.screenshot.assert_called_once_with(sentinel.path)

  def test_take_screenshot_checks_page_title(self):
    """Don't take a screenshot when the page title is unexpected."""

    mock_driver = MagicMock()
    mock_driver.title = 'foo'

    with self.assertRaises(Exception):
      MapPreview.take_screenshot(
          mock_driver,
          sentinel.path,
          time_impl=MagicMock(),
          webdriver_impl=MagicMock())

  def test_get_argument_parser(self):
    """Return an ArgumentParser."""

    result = MapPreview.get_argument_parser()
    self.assertIsInstance(result, argparse.ArgumentParser)

  def test_main(self):
    """Launch the main entry point."""

    mock_context = MagicMock()
    mock_context.__enter__.return_value = sentinel.driver
    mock_utils = MagicMock()
    mock_utils.run_screenshot_stack.return_value = mock_context

    with patch.object(MapPreview, 'take_screenshot') as mock_take_screenshot:
      MapPreview.main(sentinel.path, utils_impl=mock_utils)
      mock_take_screenshot.assert_called_once_with(
          sentinel.driver, sentinel.path)

    mock_utils.run_screenshot_stack.assert_called_once_with(
        MapPreview.SCREEN_SIZE)
