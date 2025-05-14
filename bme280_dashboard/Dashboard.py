import curses
import time


class Dashboard:

    def __init__(self, stdscr, bme280):
        self.__stdscr = stdscr
        self.__bme280 = bme280
        self.__errors = []

        self.__units = {
            "Temperature": "°C",
            "Humidity": "%",
            "Pressure": "hPa"
        }

        self.__run()


    def __run(self):
        curses.curs_set(0)
        curses.start_color()

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

        self.__stdscr.nodelay(True)
        self.__stdscr.timeout(500)

        title = "BME280 Sensor Readings"
        screen_height, screen_width = -1, -1
        readings = None

        while True:
            should_reprint = False

            if (new_readings := self.__get_bme280_readings()) != readings:
                readings = new_readings
                should_reprint = True

            if (new_dimensions := self.__stdscr.getmaxyx()) != (screen_height, screen_width):
                screen_height, screen_width = new_dimensions
                should_reprint = True

            if should_reprint:
                self.__print_content(title, readings, screen_height, screen_width)

                if self.__errors:
                    self.__print_errors(self.__errors)

            key = self.__stdscr.getch()
            if key == ord('q'):
                break


    def __print_content(self, title, readings, screen_height, screen_width):
        self.__stdscr.clear()

        self.__print_dashboard(title, readings, screen_height, screen_width)
        self.__print_bottom("Press 'q' to quit", screen_height, screen_width)

        self.__stdscr.refresh()


    def __get_bme280_readings(self):
        data = {
            "Temperature": "N/A",
            "Humidity": "N/A",
            "Pressure": "N/A"
        }
        self.__errors = []

        for key in data.keys():
            sensor_name = key.lower()
            sensor = self.__bme280.sensors.get(sensor_name)

            if sensor.value:
                data[key] = f"{sensor.value:.2f} {self.__units[key]}"
            else:
                data[key] = "N/A"
                self.__errors.append(f"Could not read inputs of {sensor_name} sensor in {self.__bme280.sensors[sensor_name].input_file}")

        return data


    def __print_dashboard(self, title, readings, screen_height, screen_width):
        table_y_offset = screen_height // 2 - len(readings)
        title_y_offset = table_y_offset - 4
        column_gap = 10

        self.__stdscr.addstr(title_y_offset, self.__get_centered_x_offset(title, screen_width), title, curses.A_BOLD)

        max_name_length, max_value_length = 0, 0
        for name, value in readings.items():
            max_name_length = max(max_name_length, len(name))
            max_value_length = max(max_value_length, len(value))

        for i, (name, value) in enumerate(readings.items()):
            name_column = name.ljust(max_name_length)
            value_column = value.ljust(max_value_length)

            row_text = (" " * column_gap).join([name_column, value_column])

            row_y_offset = table_y_offset + i * 2

            self.__stdscr.addstr(
                row_y_offset,
                self.__get_centered_x_offset(row_text, screen_width),
                name_column 
            )
            self.__stdscr.addstr(
                row_y_offset,
                self.__get_centered_x_offset(row_text, screen_width) + len(name_column) + column_gap,
                value_column,
                curses.A_BOLD
            )


    def __print_errors(self, errors):
        self.__stdscr.addstr(2, 0, "\n".join(f"    {error}" for error in errors), curses.color_pair(1))


    def __print_bottom(self, text, height, width):
        y_offset = max(0, height - 2)
        x_offset = max(0, (width - len(text)) // 2)

        self.__stdscr.addstr(y_offset, x_offset, text)


    @staticmethod
    def __get_centered_x_offset(text, screen_width):
        return (screen_width - len(text)) // 2
