import sys
from getopt import getopt
import curses
from bme280_dashboard.BME280 import BME280
from bme280_dashboard.Dashboard import Dashboard

def parse_path(path):
    return path if path.endswith('/') else path + '/'


def get_iio_path():
    iio_path_option = "iio-path"

    try:
        opts, args = getopt(sys.argv[1:], '', [f"{iio_path_option}="])
    except:
        print("Usage: ./bme280_dashboard --iio-path path/to/iio/device")
        sys.exit(2)

    if args:
        print("Error: Unexpected arguments provided.")
        print("Usage: ./bme280_dashboard --iio-path path/to/iio/device")
        sys.exit(2)

    iio_path = next((value for option, value in opts if option == "--iio-path"), None)

    return parse_path(iio_path) if iio_path else None


def main():
    bme280 = BME280(get_iio_path())
    curses.wrapper(lambda stdscr: Dashboard(stdscr, bme280))
