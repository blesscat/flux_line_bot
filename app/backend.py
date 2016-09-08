import threading

class load_filament_backend(threading.Thread):
    def __init__(self, Flux):
        super(load_filament_backend, self).__init__()
        self.Flux = Flux

    def run(self):
        main = self.Flux.maintain()
        def callback(robot_connection, status, temp):
            pass
        try:
            main.load_filament(process_callback=callback)
        except:
            pass

class unload_filament_backend(threading.Thread):
    def __init__(self, Flux):
        super(load_filament_backend, self).__init__()
        self.Flux = Flux

    def run(self):
        main = self.Flux.maintain()
        def callback(robot_connection, status, temp):
            pass
        try:
            main.unload_filament(process_callback=callback)
        except:
            pass
