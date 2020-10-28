"""Takes a screenshot of the COVIDcast map.

Extraneous UI is hidden so that the map is presentable in standalone form. The
screenshot is intended to be suitable for use in social media previews and
custom dashboards.
"""

# standard library
import argparse
import time
import urllib.parse

# third party
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver

# first party
from delphi.operations.screenshots.utils import Utils


class MapPreview:

  # URL of the COVIDcast map with predetermined signals
  URL = 'https://covidcast.cmu.edu/?' + urllib.parse.urlencode({
    'sensor': 'doctor-visits-smoothed_adj_cli',
    'level': 'county',
    'date': '20200918',
    'signalType': 'value',
    'encoding': 'color',
    'mode': 'overview',
    'region': '42003',
  })

  # width and height in pixels of the final screenshot
  SCREENSHOT_SIZE = (1800, 900)

  # width and height in pixels of the virtual screen needed to capture a
  # screenshot of the desired size (e.g. to allow room for surrounding UI
  # elements, window borders, etc)
  SCREEN_SIZE = (SCREENSHOT_SIZE[0], SCREENSHOT_SIZE[1] + 311)

  # location of the center of Allegheny county in pixels relative to the
  # top-left corner of the map
  ALLEGHENY_COUNTY_LOCATION = (1077, 372)

  def take_screenshot(driver, path, time_impl=time, webdriver_impl=webdriver):
    """Take a screenshot of the COVIDcast map.

    Parameters
    ----------
    driver : selenium.webdriver.remote.webdriver
        A webdriver instance, which is already connected to a selenium server.
    path : str
        The absolute path of the file where the screenshot is rendered.
    """

    print(f'navigating to {MapPreview.URL}')
    driver.get(MapPreview.URL)
    if 'COVIDcast' not in driver.title:
      raise Exception(f'unexpected title ({driver.title})')

    def is_loading(document):
      spinners = document.find_elements_by_class_name('loading-bg')
      return len(spinners) > 0

    print('waiting for map to load')
    WebDriverWait(driver, 10).until_not(is_loading)

    root = driver.find_elements_by_css_selector('main.root')[0]

    print('hiding extra ui')
    options = root.find_elements_by_class_name('options-container')[0]
    search = root.find_elements_by_class_name('search-container')[0]
    compare = root.find_elements_by_class_name('panel-bottom-wrapper')[0]
    driver.execute_script('arguments[0].style.display="none"', options)
    driver.execute_script('arguments[0].style.display="none"', search)
    driver.execute_script('arguments[0].style.display="none"', compare)

    print('resetting map view')
    controls = root.find_elements_by_class_name('map-controls-container')[0]
    home_button = controls.find_elements_by_class_name('pg-button')[2]
    home_button.click()
    # allow time for the animation to complete
    time_impl.sleep(5)

    print('hovering allegheny county')
    webdriver_impl.ActionChains(driver).move_to_element_with_offset(
        root, *MapPreview.ALLEGHENY_COUNTY_LOCATION).perform()
    # allow time for the county info popup to appear
    time_impl.sleep(1)

    print(f'rendering screenshot at {path}')
    root.screenshot(path)

  def get_argument_parser():
    """Define command line arguments and usage.

    Returns
    -------
    argparse.ArgumentParser
        A parser for command line arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--path',
        type=str,
        required=True,
        help='absolute path of generated screenshot (e.g. /path/name.png)')
    return parser

  def main(path, utils_impl=Utils):
    """Capture a screenshot of COVIDcast.

    Parameters
    ----------
    path : str
        The absolute path of the file where the screenshot is rendered.
    """

    with utils_impl.run_screenshot_stack(MapPreview.SCREEN_SIZE) as driver:
      MapPreview.take_screenshot(driver, path)


if __name__ == '__main__':
  args = MapPreview.get_argument_parser().parse_args()
  MapPreview.main(args.path)
