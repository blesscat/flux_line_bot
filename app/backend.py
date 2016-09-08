import os
import sys
import time
import threading

sys.path.insert(0, os.path.abspath('..'))

from flux import FLUX
from fluxclient.robot import FluxRobot, errors
from fluxclient.commands.misc import get_or_create_default_key


class load_filament_backend(threading.Thread):
    def __init__(self, Flux):
        super(load_filament_backend, self).__init__()
        self.Flux = Flux

    def run(self):
        main = self.Flux.maintain()
        try:
            def callback(robot_connection, status, temp):
                pass
            main.load_filament(process_callback=callback)
        except:
            while True:
                main.quit()
                time.sleep(1)

