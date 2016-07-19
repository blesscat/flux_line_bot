# -*- coding: utf8 -*-
import os
import sys
import requests
import json
import socket
from flask import render_template, request
from app import app

sys.path.insert(0, os.path.abspath('..'))

from flux import FLUX
from fluxclient.robot import FluxRobot
from fluxclient.commands.misc import get_or_create_default_key

list_files_set = {'list',
                  '檔案'}
status_set = {'status',
              '狀態',
              '狀況',
              '進度'}
FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])

def isin(message, message_set):
    _bool = bool({status for status in message_set if status in message})
    return _bool

def robot():
    client_key = get_or_create_default_key("./sdk_connection.pem")
    robot = FluxRobot((FLUX_ipaddr, 23811), client_key)
    return(robot)

def get_status():
    flux = robot()
    result = flux.report_play() 
    return str(result)

def list_files():
    client_key = get_or_create_default_key("./sdk_connection.pem")
    robot = FluxRobot((FLUX_ipaddr, 23811), client_key)
    result = robot.list_files("/SD")
    return str(result)

def get_message(json):
    _id, message = [json['result'][0]['content']['from']], json['result'][0]['content']['text']
    return _id, message

def send_message(to_user, content):
    url = 'https://trialbot-api.line.me/v1/events'
    headers = {
               'Content-Type': 'application/json; charset=UTF-8',
               'X-Line-ChannelID': os.environ['ChannelID'],
               'X-Line-ChannelSecret': os.environ['ChannelSecret'],
               'X-Line-Trusted-User-With-ACL': os.environ['MID']
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


@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('main.html')


@app.route("/test", methods=['GET'])
def test():
    if request.method == 'GET':
        print(type(os.environ['test12']))
        return str(os.environ['test12'])


@app.route("/g2ftest", methods=['GET'])
def g2ftest():
    if request.method == 'GET':
        os.system("flux_g2f -i tset.gcode -o test.fc")
        ls = os.popen("ls")
        print(ls)
        return str(ls)


@app.route("/add_rsa", methods=['GET'])
def add_rsa():
    if request.method == 'GET':
        Flux = FLUX((FLUX_ipaddr, 1901))
        result = Flux.add_rsa()
        return result


@app.route("/callback", methods=['GET', 'POST'])
def callback():
    if request.method == 'POST':
        js = request.get_json()
        _id, message =  get_message(js)
        if not message[:4] == 'Flux':
            message = '{0}知道什麼是"{1}"，但是{0}不說'.format(os.environ['name'], message,)
            send_message(_id, message)
            return 'post'
        else:
            if isin(message, status_set):
                Flux = FLUX((FLUX_ipaddr, 1901))
                Flux.status['st_prog'] = format(Flux.status['st_prog'], '.2%')

                message = '喵～～\n目前狀態:{}\n目前進度:{}'.format(
                            Flux.status['st_label'], Flux.status['st_prog'])
                send_message(_id, message)
                return 'ok'

            if isin(message, list_files_set):
                payload = list_files()
                send_message(_id, payload)
                return 'ok'

            if message == 'test':
                payload = get_status()
                send_message(_id, payload)
                return 'ok'

    if request.method == 'GET':
        Flux = FLUX((FLUX_ipaddr, 1901))

        message = str(Flux.status)
        re = send_message(['u96e32e17ebdedd21c1f84bbbfd7de08c'], message)
        return re
