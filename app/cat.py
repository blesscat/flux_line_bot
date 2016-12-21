import os
import sys
import time
import socket
import redis
from rq import Worker, Queue, Connection

sys.path.insert(0, os.path.abspath('.'))

from flux import FLUX
from app.views import line_bot_api, LINEID

from linebot.models import TextSendMessage

class watchcat(threading.Thread):
    def __init__(self):
        super(watchcat, self).__init__()
        self.daemon = True
        self.monitor = True
        self.flux_is_running = False
        self.request_count = 0

    def run(self):
        while True:
            Flux = FLUX((FLUX_ipaddr, 1901))
            message = '{}'.format(Flux.status)
            #line_bot_api.push_message(LINEID, TextSendMessage(text=message))
            time.sleep(600)

cat = watchcat()
cat.daemon = True
cat.start()

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://172.17.0.2:6379')

conn = redis.from_url(redis_url)

FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
#while True:
#    Flux = FLUX((FLUX_ipaddr, 1901))
#    message = '{}'.format(Flux.status)
    #line_bot_api.push_message(LINEID, TextSendMessage(text=message))
if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
