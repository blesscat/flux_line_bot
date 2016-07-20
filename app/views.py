# -*- coding: utf8 -*-
import os
import sys
import requests
import json
import socket
import math
from flask import render_template, request
from app import app

sys.path.insert(0, os.path.abspath('..'))

from flux import FLUX
from fluxclient.robot import FluxRobot
from fluxclient.commands.misc import get_or_create_default_key

start_list = {'start',
              '開始'}

pause_list = {'pause',
              '暫停'}

resume_list = {'resume',
               '繼續'}

abort_list = {'about',
              'stop',
              'STOP',
              '停止',
              '結束'}

list_files_set = {'list',
                  '檔案'}

status_set = {'status',
              '狀態',
              '狀況',
              '進度'}

FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
MANTRA = os.environ['mantra']
NAME = os.environ['name']

def isin(message, message_set):
    _bool = bool({status for status in message_set if status in message})
    return _bool

def robot():
    client_key = get_or_create_default_key("./sdk_connection.pem")
    robot = FluxRobot((FLUX_ipaddr, 23811), client_key)
    return robot

def get_flux_status(robot):
    payload = robot.report_play()
    timeCost = math.floor(float(robot.play_info()[0]['TIME_COST']))
    prog = float(format(payload['prog'], '.2%'))
    label = payload['st_label']
    error = payload['error']

    interval = timeCost * (1 - prog)
    secPerMins = 60
    secPerHours = secPerMins * 60
    hours = math.floor(interval/secPerHours)
    interval = interval - hours * secPerHours
    mins = math.floor(interval/secPerMins)
    leftTime = '{} hours {} mins'.format(hours, mins)

    return label, prog, error, leftTime

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
            message = '{0}知道什麼是"{1}"，但是{0}不說'.format(NAME, message,)
            send_message(_id, message)
            return 'post'
        else:
            Flux = robot()
            if Flux.report_play()['st_label'] == 'IDLE':
                message = '{}\nFLUX目前閒置中喔'.format(MANTRA)
                send_message(_id, message)
                return 'ok' 

            if Flux.report_play()['st_label'] == 'COMPLETED':
                message = '{}\nFLUX工作已經完成了呢！！'.format(MANTRA)
                send_message(_id, message)
                return 'ok' 

            label, prog, error, leftTime = get_flux_status(Flux)

            if isin(message, status_set):
                message = '{}\n目前狀態: {}\n目前進度: {}\n剩餘時間:{}'.format(
                            MANTRA, label, prog, leftTime)
                send_message(_id, message)

            if isin(message, start_list):
                try:
                    message = '{}\n開始功能還沒做喔～～'.format(MANTRA)
                    send_message(_id, message)
                except:
                    pass
            if isin(message, pause_list):
                try:
                    Flux.pause_play()
                    message = '{}\n已經暫停了喔'.format(MANTRA)
                    send_message(_id, message)
                except:
                    message = '{}\n無法暫停，可能已經停止了'.format(MANTRA)
                    send_message(_id, message)
            if isin(message, resume_list):
                try:
                    Flux.resume_play()
                    message = '{}\n已經繼續在印了呢'.format(MANTRA)
                    send_message(_id, message)
                except:
                    message = '{}\n無法繼續，可能已經停止了'.format(MANTRA)
                    send_message(_id, message)

            if isin(message, abort_list):
                try:
                    Flux.resume_play()
                    message = '{}\n已經暫停囉'.format(MANTRA)
                    send_message(_id, message)
                except:
                    message = '{}\n無法暫停，可能早就已經停止了呢'.format(MANTRA)
                    send_message(_id, message)

            if isin(message, list_files_set):
                _list = str(Flux.list_files('/SD'))
                message = '{}'.format(_list)
                send_message(_id, message)

            Flux.close()
            return 'ok'

    if request.method == 'GET':
        Flux = FLUX((FLUX_ipaddr, 1901))

        message = str(Flux.status)
        re = send_message(['u96e32e17ebdedd21c1f84bbbfd7de08c'], message)
        return re
