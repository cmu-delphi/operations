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
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.operations.screenshots.utils import Utils


class MapPreviewException(Exception):
  """Raised for exceptions specific to the `MapPreview` class."""


class MapPreview:

  # URL of the COVIDcast map
  BASE_URL = 'https://covidcast.cmu.edu/'

  # Horizontal and vertical padding, in pixels, required to accomodate a
  # screenshot of a given size, accounting for extraneous UI elements.
  SCREEN_PADDING = (0, 311)

  def get_most_recent_date(
      source, signal, geo_type, geo_value, epidata_impl=Epidata):
    """Get the date of most recently available data for a given signal.

    Parameters
    ----------
    source : str
        COVIDcast data source.
    signal : str
        COVIDcast signal name.
    geo_type : str
        COVIDcast geographic resolution.
    geo_value : str
        COVIDcast location name.

    Returns
    -------
    str
        Date of most recent data in YYYYMMDD format.

    Raises
    ------
    MapPreviewException
        If there is no data for the signal.
    """

    # Query `covidcast` directly because `covidcast_meta` aggregates over all
    # locations, and the given location may not have data as recent as some
    # other location for the same signal.
    date_range = Epidata.range(20200101, 20500101)
    response = epidata_impl.covidcast(
        source, signal, 'day', geo_type, date_range, geo_value)
    if response['result'] != 1:
      raise MapPreviewException(
          f'unable to get most recent date for {source} {signal}')

    most_recent = max(row['time_value'] for row in response['epidata'])
    return str(most_recent)

  def take_screenshot(
      driver, args, resolved_date, time_impl=time, webdriver_impl=webdriver):
    """Take a screenshot of the COVIDcast map.

    Parameters
    ----------
    driver : selenium.webdriver.remote.webdriver
        A webdriver instance, which is already connected to a selenium server.
    args : argparse.Namespace
        Command-line arguments.
    resolved_date : str
        Date of the signal in YYYYMMDD format.

    Raises
    ------
    MapPreviewException
        If interaction with the webpage fails.
    """

    URL = MapPreview.BASE_URL + '?' + urllib.parse.urlencode({
      'sensor': f'{args.source}-{args.signal}',
      'level': args.geo_type,
      'region': args.geo_value,
      'date': resolved_date,
    })

    print(f'navigating to {URL}')
    driver.get(URL)
    if 'COVIDcast' not in driver.title:
      raise MapPreviewException(f'unexpected title ({driver.title})')

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

    hover_location = (args.hover_x, args.hover_y)
    print(f'hovering mouse at {hover_location}')
    webdriver_impl.ActionChains(driver).move_to_element_with_offset(
        root, *hover_location).perform()
    # allow time for the county info popup to appear
    time_impl.sleep(1)

    print(f'rendering screenshot at {args.path}')
    root.screenshot(args.path)

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
    parser.add_argument(
        '--source',
        type=str,
        default='doctor-visits',
        help='COVIDcast data source (default \'doctor-visits\')')
    parser.add_argument(
        '--signal',
        type=str,
        default='smoothed_adj_cli',
        help='COVIDcast signal name (default \'smoothed_adj_cli\')')
    parser.add_argument(
        '--geo_type',
        type=str,
        default='county',
        help='COVIDcast geographic resolution (default \'county\')')
    parser.add_argument(
        '--geo_value',
        type=str,
        default='42003',
        help='COVIDcast location name (default \'42003\')')
    parser.add_argument(
        '--date',
        type=str,
        help=(
          'date of the signal in YYYYMMDD format; if unspecified, use the '
          'most recent date for the signal'
        ))
    parser.add_argument(
        '--width',
        type=int,
        default=1800,
        help='width of the screenshot, in pixels (default 1800)')
    parser.add_argument(
        '--height',
        type=int,
        default=900,
        help='height of the screenshot, in pixels (default 900)')
    parser.add_argument(
        '--hover_x',
        type=int,
        default=0,
        help=(
          'horizontal location to mouse hover, '
          'in pixels relative to top-left (default 0)'
        ))
    parser.add_argument(
        '--hover_y',
        type=int,
        default=0,
        help=(
          'vertical location to mouse hover, '
          'in pixels relative to top-left (default 0)'
        ))
    return parser

  def main(args, utils_impl=Utils):
    """Capture a screenshot of COVIDcast.

    Parameters
    ----------
    args : argparse.Namespace
        Command-line arguments.
    """

    if args.date:
      resolved_date = args.date
    else:
      resolved_date = MapPreview.get_most_recent_date(
          args.source, args.signal, args.geo_type, args.geo_value)
    print(f'using latest data reported for date {resolved_date}')

    screen_size = (
      args.width + MapPreview.SCREEN_PADDING[0],
      args.height + MapPreview.SCREEN_PADDING[1],
    )
    with utils_impl.run_screenshot_stack(screen_size) as driver:
      MapPreview.take_screenshot(driver, args, resolved_date)


if __name__ == '__main__':
  MapPreview.main(MapPreview.get_argument_parser().parse_args())
