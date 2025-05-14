import sys
import threading
import time
import curses

class Monitor:
    def __init__(self, base=None):
        self.base = base or "/sys/devices/platform/soc/fe804000.i2c/i2c-1/1-0077/iio:device0/"
        if not self.base.endswith('/'):
            self.base += '/'
        self.sensors = {'temp': None, 'hum': None, 'pres': None}
        self._stop = False
        self._thr = threading.Thread(target=self._run)
        self._thr.start()

    def _run(self):
        while not self._stop:
            for key, fname in [('temp','in_temp_input'),('hum','in_humidityrelative_input'),('pres','in_pressure_input')]:
                try:
                    with open(self.base+fname) as f:
                        self.sensors[key] = float(f.read().strip())/1000.0
                except:
                    self.sensors[key] = None
            time.sleep(1)

    def latest(self):
        return self.sensors.copy()

    def stop(self):
        self._stop = True
        self._thr.join()

def main():
    iio = None
    if len(sys.argv) > 1 and sys.argv[1].startswith('--path='):
        iio = sys.argv[1].split('=',1)[1]
    m = Monitor(iio)
    try:
        curses.wrapper(__loop, m)
    except KeyboardInterrupt:
        pass
    finally:
        m.stop()


def __loop(stdscr, m):
    stdscr.nodelay(True)
    stdscr.timeout(500)
    while True:
        stdscr.clear()
        d = m.latest()
        stdscr.addstr(1,2, f"T: {d['temp']} C")
        stdscr.addstr(2,2, f"H: {d['hum']} %")
        stdscr.addstr(3,2, f"P: {d['pres']} hPa")
        stdscr.addstr(5,2, "q zum Beenden")
        if stdscr.getch() == ord('q'):
            break
        stdscr.refresh()
        curses.napms(500)

if __name__ == '__main__':
    main()
