import os
import socket
import requests
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
        self.FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
        self.mantra = os.environ['mantra']
        self.name = os.environ['name']
        self.LineID = os.environ.get('LineID', 'test')
        self.ChannelAccessToken = os.environ.get('ChannelAccessToken')
        self.ChannelSecret = os.environ.get('ChannelSecret')
        self._id = _id
        self.message = message
        self.command_list = '\n'.join(flux_command_list)
