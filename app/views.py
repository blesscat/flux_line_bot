# -*- coding: utf8 -*-
import os
import sys
import requests
import json
from flask import render_template, request, jsonify
from app import app

sys.path.insert(0, os.path.abspath('..'))

from flux import FLUX
from fluxclient.robot import FluxRobot
from fluxclient.commands.misc import get_or_create_default_key

status_set = {'status',
              '狀態',
              '狀況',
              '進度'}

FLUX_ipaddr = "122.116.80.243"


@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('main.html')


@app.route("/test", methods=['GET'])
def test():
    if request.method == 'GET':
        client_key = get_or_create_default_key("./sdk_connection.pem")
        robot = FluxRobot((FLUX_ipaddr, 23811), client_key)
        print(robot.list_files('/SD'))
        return str(robot.play_info())


@app.route("/add_rsa", methods=['GET'])
def add_rsa():
    if request.method == 'GET':
        Flux = FLUX((FLUX_ipaddr, 1901))
        result = Flux.add_rsa()
        return result


@app.route("/callback", methods=['GET', 'POST'])
def callback():
    def get_message(json):
        _id, message = [json['result'][0]['content']['from']], json['result'][0]['content']['text']
        return _id, message

    def send_message(to_user, content):
        url = 'https://trialbot-api.line.me/v1/events'
        headers = {
                   'Content-Type': 'application/json; charset=UTF-8',
                   'X-Line-ChannelID': '1473077665',
                   'X-Line-ChannelSecret': '8582629c37b18605491087172be06e5e',
                   'X-Line-Trusted-User-With-ACL': 'u3425f8daf2f07f3a9d723f5232f50f63'
                  }
        data = {
                'to': to_user,
                'toChannel': 1383378250,
                'eventType': '138311608800106203',
                'content': {
                    'contentType': 1,
                    'toType': 1,
                    'text': content
                    }
               }
        r = requests.post(url, data=json.dumps(data), headers=headers)
        return json.dumps(r.json(), indent=4)

    if request.method == 'POST':
        js = request.get_json()
        _id, message =  get_message(js)
        if _id == ['u96e32e17ebdedd21c1f84bbbfd7de08c']:
            if not message[:4] == 'Flux':
                message = '{}{}{}'.format('豬毛', message, '，但是豬毛不說')
                send_message(_id, message)
                return 'post'
            else:
                if bool({status for status in status_set if status in message}):
                    Flux = FLUX((FLUX_ipaddr, 1901))
                    Flux.status['st_prog'] = format(Flux.status['st_prog'], '.2%')

                    message = '喵～～\n目前狀態:{}\n目前進度:{}'.format(
                                Flux.status['st_label'], Flux.status['st_prog'])
                    send_message(_id, message)
                    return 'ok'
        else:
            message = '{}{}{}'.format('豬毛', message, '，但是豬毛不說')
            send_message(_id, message)
            return 'ok'

    if request.method == 'GET':
        Flux = FLUX((FLUX_ipaddr, 1901))

        message = str(Flux.status)
        re = send_message(['u96e32e17ebdedd21c1f84bbbfd7de08c'], message)
        return re
