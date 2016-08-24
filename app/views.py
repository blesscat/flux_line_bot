# -*- coding: utf8 -*-
import os
import sys
import requests
import json
import socket
import math
import time
from flask import render_template, request
from app import app

sys.path.insert(0, os.path.abspath('..'))

from flux import FLUX
from fluxclient.robot import FluxRobot, errors
from fluxclient.commands.misc import get_or_create_default_key

status_set = {'110',
              'status',
              'STATUS',
              '狀態',
              '狀況',
              '進度'}

list_files_set = {'120',
                  'list',
                  'LIST',
                  '檔案'}

start_set = {'210',
             'start',
             'START',
             '開始'}

pause_set = {'220',
             'pause',
             'PAUSE',
             '暫停'}

resume_set = {'230',
              'resume',
              'RESUME',
              '繼續'}

abort_set = {'240',
             'abort',
             'ABORT',
             'stop',
             'STOP',
             '停止',
             '結束'}

FLUX_COMMANDS=""
flux_command_list = ["110 - status",
                     "120 - list_files",
                     "210 - start",
                     "220 - pause",
                     "230 - resume",
                     "240 - abort"]
for command in flux_command_list:
    FLUX_COMMANDS += command + '\n'

FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
MANTRA = os.environ['mantra']
NAME = os.environ['name']

PICTURE = "https://4.bp.blogspot.com/-v1BgHwzoVeo/V709k2CmubI/" + \
          "AAAAAAAAI_Q/qfmZHxOhrwAfzOAUAJtHe-WPmSKNL3wIwCPcB/s1600/picture.jpg"

def isin(message, message_set):
    _bool = bool({status for status in message_set if status in message})
    return _bool


def robot():
    client_key = get_or_create_default_key("./sdk_connection.pem")
    try:
        robot = FluxRobot((FLUX_ipaddr, 23811), client_key)
    except errors.RobotSessionError:
        add_rsa()
        robot = FluxRobot((FLUX_ipaddr, 23811), client_key)
    return robot


def get_flux_status(robot):
    payload = robot.report_play()
    timeCost = math.floor(float(robot.play_info()[0]['TIME_COST']))
    prog = float(payload['prog'])
    label = payload['st_label']
    error = payload['error']
    try:
        interval = timeCost * (1 - prog)
        secPerMins = 60
        secPerHours = secPerMins * 60
        hours = math.floor(interval/secPerHours)
        interval = interval - hours * secPerHours
        mins = math.floor(interval/secPerMins)
        leftTime = '{} hours {} mins'.format(hours, mins)
        prog = format(prog, '.2%')
    except ValueError:
        prog = 'unknow'
        leftTime = 'FLUX不告訴我啦！'

    return label, prog, error, leftTime


def get_message(json):
    _id = [json['result'][0]['content']['from']] 
    message = json['result'][0]['content']['text']
    contentType = json['result'][0]['content']['contentType']

    return _id, message, contentType


def add_rsa():
    Flux = FLUX((FLUX_ipaddr, 1901))
    result = Flux.add_rsa()
    return result


def isin_status(Flux):
    status = Flux.report_play()['st_label']
    if status == 'RUNNING':  
        label, prog, error, leftTime = get_flux_status(Flux)
        message = '{}\n目前狀態: {}\n目前進度: {}\n剩餘時間: {}'.format(
                   MANTRA, label, prog, leftTime)
    elif status == 'IDLE':
        message = '{}\nFLUX目前閒置中喔'.format(MANTRA)
    elif status == 'COMPLETED':
        message = '{}\nFLUX工作已經完成了呢！！'.format(MANTRA)
    else:       
        message = '{}\n目前狀態{}'.format(MANTRA, status)

    return message


def isin_pause(Flux):
    try:
        Flux.pause_play()
        message = '{}\n已經暫停了喔'.format(MANTRA)
    except:
        message = '{}\n無法暫停，可能已經停止了'.format(MANTRA)
    return message


def isin_resume(Flux):
    try:
        Flux.resume_play()
        message = '{}\n已經繼續在印了呢'.format(MANTRA)
    except:
        message = '{}\n無法繼續，可能已經停止了'.format(MANTRA)
    return message


def isin_abort(Flux):
    try:
        Flux.abort_play()
        message = '{}\n已經停止囉'.format(MANTRA)
    except:
        message = '{}\n無法停止，可能早就已經停止了呢'.format(MANTRA)
    return message


def isin_list_files(Flux):
    _list = str(Flux.list_files('/SD'))
    message = '{}'.format(_list)
    return message


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


@app.route("/", methods=['GET'])
def index():
   if request.method == 'GET':
       return render_template('main.html')


@app.route("/upload_file", methods=['GET'])
def upload_file():
   if request.method == 'GET':
       os.system("python setup.py install")
       return 'main.html'


@app.route("/callback", methods=['POST'])
def callback():
    if request.method == 'POST':
        js = request.get_json()
        _id, message, contentType = get_message(js)
        if contentType != 1:
            send_picture(_id)
            return "ok"
        if message == '罐罐':
            message = '{0}要吃罐罐！！\n{0}要吃罐罐！！\n給{0}吃！！'.format(NAME)
            send_message(_id, message)
            time.sleep(5)
            message = '{}\n{}能做的工作如下喔!\n{}'.format(MANTRA, NAME, FLUX_COMMANDS)
            send_message(_id, message)
            return 'ok'
        
        magic_id = message[:5].lower()
        if magic_id == 'flux ' or magic_id == '8763 ':
            Flux = robot()
 
            if isin(message, status_set):
                message = isin_status(Flux)
 
            elif isin(message, list_files_set):
                message = isin_list_files(Flux)

            elif isin(message, start_set):
                message = '{}\n開始功能還沒完成喔～～'.format(MANTRA)
 
            elif isin(message, pause_set):
                message = isin_pause(Flux)
 
            elif isin(message, resume_set):
                message = isin_resume(Flux)
 
            elif isin(message, abort_set):
                message = isin_abort(Flux)
 
            else :
                message = '{}\n{}不知道"{}"是什麼啦！'.format(MANTRA, NAME, message[5:])
 
            send_message(_id, message)
            Flux.close()
            return 'ok'

        else:
            message = '{0}知道什麼是"{1}"，但是{0}不說'.format(NAME, message)
            send_message(_id, message)
            return 'ok'
