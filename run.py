from app import app, watchdog
import builtins

builtins.dog = watchdog.watchdog()
builtins.dog.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
