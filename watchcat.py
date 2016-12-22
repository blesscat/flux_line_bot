import os
import sys
import time
import threading
import requests

from rq import Worker, Queue, Connection

sys.path.insert(0, os.path.abspath('.'))

from app.utils import assistant, line_bot_api, conn, listen, LANG
from flux import FLUX
from linebot.models import TextSendMessage


class watchcat(threading.Thread):
    def __init__(self):
        super(watchcat, self).__init__()
        self.daemon = True
        self.monitor = True
        self.flux_is_running = False
        self.request_count = 0
        self.assist = assistant()

    def run(self):
        while self.monitor:
            try:
                self.monitor_flux_status()
            except:
                continue
            #self.make_heroku_wakeup()
            time.sleep(1)


    def monitor_flux_status(self):
        self.Flux = FLUX((self.assist.FLUX_ipaddr, 1901))
        self.status = self.Flux.status.get('st_label', 'none')
        self.error = self.Flux.status.get('error_label', '')
        print(self.status)
        if self.status == 'ST_RUNNING':
            if not self.flux_is_running:
                self.flux_is_running = True
                message = '{}\nFLUX開始工作了喔～～'.format(self.assist.mantra)
                line_bot_api.push_message(self.LINEID, TextSendMessage(text=message))

        elif self.status == 'none':
            pass

        else:
            if self.flux_is_running:
                self.flux_is_running = False
                message = self.flux_stop_analysis()
                line_bot_api.push_message(self.assist.LineID, TextSendMessage(text=message))

    def flux_stop_analysis(self):
        if self.status == 'ST_PAUSED' or self.status == 'ST_PAUSING':
            if self.error != '':
                message = '{}\nFLUX停止了!\n停止原因: {}'.format(self.assist.mantra, self.error)
            elif self.error == '':
                message = '{}\nFLUX暫停囉～'.format(self.assist.mantra)

        elif self.status == 'ST_COMPLETED' or self.status == 'ST_IDLE' or \
                        self.status == 'ST_COMPLETEING':
            message = '{}\n工作已經完成了喔!'.format(self.assist.mantra)
        
        else:
           message = '{}\nFLUX因為 {} 停止了!'.format(self.assist.mantra, self.error)
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

    def _start(self):
        self.monitor = True

    def stop(self):
        self.monitor = False

    def status(self):
        return self.monitor

cat = watchcat()
cat.start()


if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
