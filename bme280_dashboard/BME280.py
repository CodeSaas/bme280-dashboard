import threading
import time

FALLBACK_IIO_PATH = "/sys/devices/platform/soc/fe804000.i2c/i2c-1/1-0077/iio:device0/"
HUMIDITY_INPUT_FILE = "in_humidityrelative_input"
PRESSURE_INPUT_FILE = "in_pressure_input"
TEMPERATURE_INPUT_FILE = "in_temp_input"

UPDATE_INTERVAL = 1.0


class BME280Sensor:

    def __init__(self, value, input_file):
        self.value: float | None = value 
        self.input_file = input_file


class BME280:

    def __init__(self, iio_path=None):
        self.__iio_path = iio_path or FALLBACK_IIO_PATH
        self.__update_interval = UPDATE_INTERVAL
        self.__stop_event = threading.Event()
        self.__thread = threading.Thread(target=self.__update_loop, daemon=True)

        self.sensors = {
            "temperature": BME280Sensor(None, TEMPERATURE_INPUT_FILE),
            "humidity": BME280Sensor(None, HUMIDITY_INPUT_FILE),
            "pressure": BME280Sensor(None, PRESSURE_INPUT_FILE),
        }

        for sensor_name in self.sensors.keys():
            self.__update_sensor_value(sensor_name)

        self.__thread.start()

    def stop(self):
            self.__stop_event.set()
            self.__thread.join()


    def __update_loop(self):
        while not self.__stop_event.is_set():
            for sensor_name in self.sensors:
                self.__update_sensor_value(sensor_name)
            time.sleep(self.__update_interval)


    def __update_sensor_value(self, sensor_name):
        sensor = self.sensors[sensor_name]

        try:
            sensor.value = self.__string_input_to_float(
                self.__read_file(f"{self.__iio_path}{sensor.input_file}")
            )
        except:
            sensor.value = None


    @staticmethod
    def __string_input_to_float(string_input):
        return float(string_input) / 1000. if string_input is not None else None


    @staticmethod
    def __read_file(filename):
        with open(filename, 'r') as f:
            return f.read().strip()
