import threading
import time

SENSOR_DIR = "/sys/devices/platform/soc/fe804000.i2c/i2c-1/1-0077/iio:device0"
UPDATE_SEC = 1.0

class Sensor:
    def __init__(self, name, fname):
        self.name = name
        self.fname = fname
        self.value = None

    def read(self, base):
        try:
            with open(f"{base}/{self.fname}") as f:
                raw = f.read().strip()
            self.value = float(raw) / 1000.0
        except:
            self.value = None

class Monitor:
    def __init__(self, path=None):
        self.path = path or SENSOR_DIR
        self.sensors = [
            Sensor('temp', 'in_temp_input'),
            Sensor('hum', 'in_humidityrelative_input'),
            Sensor('pres', 'in_pressure_input')
        ]
        self._stop = False
        self.thread = threading.Thread(target=self._run)
        for s in self.sensors:
            s.read(self.path)
        self.thread.start()

    def _run(self):
        while not self._stop:
            for s in self.sensors:
                s.read(self.path)
            time.sleep(UPDATE_SEC)

    def stop(self):
        self._stop = True
        self.thread.join()

    def latest(self):
        return {s.name: s.value for s in self.sensors}

if __name__ == '__main__':
    m = Monitor()
    try:
        while True:
            d = m.latest()
            print(f"Temp={d['temp']}, Hum={d['hum']}, Pres={d['pres']}")
            time.sleep(5)
    except KeyboardInterrupt:
        m.stop()
