import os
import socket
import requests
import json
import redis

#from watchcat import conn
from app import app
from linebot import  LineBotApi, WebhookHandler
from rq import Queue

ChannelAccessToken = os.environ.get('ChannelAccessToken')
ChannelSecret = os.environ.get('ChannelSecret')

line_bot_api = LineBotApi(ChannelAccessToken)
handler = WebhookHandler(ChannelSecret)

lang_file = 'zh_tw.json'
lang_dir_path = os.path.join(app.static_folder, 'lang')

with open(os.path.join(lang_dir_path, lang_file)) as f:
    LANG = json.load(f)

listen = ['high', 'default', 'low']
redis_url = os.getenv('REDISTOGO_URL', 'redis://172.17.0.2:6379')
conn = redis.from_url(redis_url)

backjob = Queue(connection=conn)

flux_command_list = ["110 - status",
                     "120 - list_files",
                     "130 - watchdog",
                     "131 - watchdogon",
                     "132 - watchdogoff",
                     "210 - start",
                     "211 - startweb",
                     "212 - startfs",
                     "220 - pause",
                     "230 - resume",
                     "240 - abort",
                     "250 - quit"]


def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())

class assistant(object):
    def __init__(self, _id='', message=''):
        self.fb_token = 'blesscat'
        self.fb_page_access_token = os.environ["PAGE_ACCESS_TOKEN"]
        self.FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
        self.mantra = os.environ['mantra']
        self.name = os.environ['name']
        self.LineID = os.environ.get('LineID', 'test')
        self.ChannelAccessToken = os.environ.get('ChannelAccessToken')
        self.ChannelSecret = os.environ.get('ChannelSecret')
        self._id = _id
        self.message = message
        self.command_list = '\n'.join(flux_command_list)
