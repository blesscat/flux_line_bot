import os
import socket
import requests

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())

class assistant(object):
    def __init__(self, _id, message):
        self.fb_token = 'blesscat'
        self.FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
        self.mantra = os.environ['mantra']
        self.name = os.environ['name']
        self.LINEID = os.environ.get('LineID', 'test')
        self.ChannelAccessToken = os.environ.get('ChannelAccessToken')
        self.ChannelSecret = os.environ.get('ChannelSecret')
        self._id = _id
        self.message = message
