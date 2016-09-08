import os
import sys
import time
import threading
from app import line

sys.path.insert(0, os.path.abspath('..'))

from flux import FLUX
from fluxclient.robot import FluxRobot, errors
from fluxclient.commands.misc import get_or_create_default_key

_id_ = os.environ.get('LineID', 'none')
_id = [_id_]
MANTRA = os.environ['mantra']


class load_filament_backend(threading.Thread):
    def __init__(self, Flux):
        super(load_filament_backend, self).__init__()
        self.Flux = Flux

    def run(self):
        main = self.Flux.maintain()
        try:
            message = '{}\nFLUX加溫中～～'.format(MANTRA)
            line.send_message(_id, message)
            def callback(robot_connection, status, temp):
                pass
            main.load_filament(process_callback=callback)
        except:
            for i in range(20):
                try:
                    message = '{}\nFLUX{}'.format(MANTRA, i)
                    line.send_message(_id, message)
                    print(i)
                    main.quit()
                    time.sleep(1)
                except:
                    pass

