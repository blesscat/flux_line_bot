import requests
import json
import os

from app import app

PICTURE = "https://4.bp.blogspot.com/-v1BgHwzoVeo/V709k2CmubI/" + \
          "AAAAAAAAI_Q/qfmZHxOhrwAfzOAUAJtHe-WPmSKNL3wIwCPcB/s1600/picture.jpg"

def send_message(_id, message):
    url = 'https://trialbot-api.line.me/v1/events'
    headers = {
               'Content-Type': 'application/json; charset=UTF-8',
               'X-Line-ChannelID': os.environ['ChannelID'],
               'X-Line-ChannelSecret': os.environ['ChannelSecret'],
               'X-Line-Trusted-User-With-ACL': os.environ['MID']
              }
    data = {
            'to': _id,
            'toChannel': 1383378250,
            'eventType': '138311608800106203',
            'content': {
                'contentType': 1,
                'toType': 1,
                'text': message
                }
           }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return json.dumps(r.json(), indent=4)


def send_picture(_id):
    url = 'https://trialbot-api.line.me/v1/events'
    headers = {
               'Content-Type': 'application/json; charset=UTF-8',
               'X-Line-ChannelID': os.environ['ChannelID'],
               'X-Line-ChannelSecret': os.environ['ChannelSecret'],
               'X-Line-Trusted-User-With-ACL': os.environ['MID']
              }
    data = {
            'to': _id,
            'toChannel': 1383378250,
            'eventType': '138311608800106203',
            'content': {
                'contentType': 2,
                'toType': 1,
                "originalContentUrl": PICTURE,
                "previewImageUrl": PICTURE
                }
           }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return json.dumps(r.json(), indent=4)
