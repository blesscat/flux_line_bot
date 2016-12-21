import os
import sys
import time
import socket
import threading
import redis
import requests

from rq import Worker, Queue, Connection

sys.path.insert(0, os.path.abspath('.'))

from flux import FLUX
from app.views import line_bot_api, LINEID, MANTRA
from linebot.models import TextSendMessage


class watchcat(threading.Thread):
    def __init__(self):
        super(watchcat, self).__init__()
        self.daemon = True
        self.monitor = True
        self.flux_is_running = False
        self.request_count = 0
        self.FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])

    def run(self):
        while self.monitor:
            try:
                self.monitor_flux_status()
            except:
                continue
            self.make_heroku_wakeup()
            time.sleep(1)


    def monitor_flux_status(self):
        FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
        self.Flux = FLUX((FLUX_ipaddr, 1901))
        self.status = self.Flux.status.get('st_label', 'none')
        self.error = self.Flux.status.get('error_label', '')
        if self.status == 'ST_RUNNING':
            if not self.flux_is_running:
                self.flux_is_running = True
                message = '{}\nFLUX開始工作了喔～～'.format(MANTRA)
                line_bot_api.push_message(LINEID, TextSendMessage(text=message))

        elif self.status == 'none':
            pass

        else:
            if self.flux_is_running:
                self.flux_is_running = False
                message = self.flux_stop_analysis()
                line_bot_api.push_message(LINEID, TextSendMessage(text=message))

    def flux_stop_analysis(self):
        if self.status == 'ST_PAUSED' or self.status == 'ST_PAUSING':
            if self.error != '':
                message = '{}\nFLUX停止了!\n停止原因: {}'.format(MANTRA, self.error)
            elif self.error == '':
                message = '{}\nFLUX暫停囉～'.format(MANTRA)

        elif self.status == 'ST_COMPLETED' or self.status == 'ST_IDLE' or \
                        self.status == 'ST_COMPLETEING':
            message = '{}\n工作已經完成了喔!'.format(MANTRA)
        
        else:
           message = '{}\nFLUX因為 {} 停止了!'.format(MANTRA, self.error)
        return message


    def make_heroku_wakeup(self):
        self.request_count += 1
        if self.request_count >= 300:
            while True:
                r = requests.get(os.environ['WEB_URL'])
                time.sleep(1)
                if r._content == b'main':
                    break
            self.request_count = 0

    def start(self):
        self.monitor = True

    def stop(self):
        self.monitor = False

    def status(self):
        return self.monitor

cat = watchcat().start()

listen = ['high', 'default', 'low']
redis_url = os.getenv('REDISTOGO_URL', 'redis://172.17.0.2:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
