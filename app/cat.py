import os
import time
import socket

from flux import FLUX
from .views import line_bot_api, LINEID

from linebot.models import TextSendMessage


FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
while True:
    Flux = FLUX((FLUX_ipaddr, 1901))
    message = '{}'.format(Flux.status)
    print(message)
    line_bot_api.push_message(LINEID, TextSendMessage(text=message))
    time.sleep(600)
