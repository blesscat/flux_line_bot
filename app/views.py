# -*- coding: utf8 -*-
import os
import sys
import requests
import json
import socket
import math
import time
from flask import render_template, request
from werkzeug import secure_filename
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

web_set = {'211',
           'web',
           'WEB'}

fs_set = {'212',
          'fs',
          'FS'}

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

FLUX_COMMANDS = ""
flux_command_list = ["110 - status",
                     "120 - list_files",
                     "210 - start",
                     "211 - web",
                     "212 - fs",
                     "220 - pause",
                     "230 - resume",
                     "240 - abort"]
for command in flux_command_list:
    FLUX_COMMANDS += command + '\n'

FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
MANTRA = os.environ['mantra']
NAME = os.environ['name']
LINEID = os.environ.get('lineID', '')
os.environ['passed'] = "False"

PICTURE = "https://4.bp.blogspot.com/-v1BgHwzoVeo/V709k2CmubI/" + \
          "AAAAAAAAI_Q/qfmZHxOhrwAfzOAUAJtHe-WPmSKNL3wIwCPcB/s1600/picture.jpg"


def allowed_file(filename, allowed_file):
    if allowed_file is "fc":
        allowed_extensions = app.config['FC_ALLOWED_EXTENSIONS']
    else:
        allowed_extensions = set([])
    bool_allow = '.' in filename and \
                 filename.rsplit('.', 1)[1] in allowed_extensions
    return bool_allow


def isin(message, message_set):
    _bool = bool({status for status in message_set if status in message})
    return _bool


def upload_callback(robot_connection, sent, size):
    print('sent: {}'.format(sent))
    print('size: {}'.format(size))


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
    report = Flux.report_play()
    status = report['st_label']
    error = report['error']
    if status == 'RUNNING':
        label, prog, error, leftTime = get_flux_status(Flux)
        message = '{}\n目前狀態: {}\n目前進度: {}\n剩餘時間: {}'.format(
                   MANTRA, label, prog, leftTime)
    elif status == 'IDLE':
        message = '{}\nFLUX目前閒置中喔'.format(MANTRA)
    elif status == 'COMPLETED':
        message = '{}\nFLUX工作已經完成了呢！！'.format(MANTRA)
    elif status == 'WAITING_HEAD':
        message = '{}\nFLUX正在校正中呢，等他一下喔～'.format(MANTRA)
    elif status == 'PAUSING':
        message = '{}\nFLUX停止了！\n停止的原因是: {}'.format(MANTRA, error)
    elif status == 'PAUSED':
        message = '{}\nFLUX已經停止。\n停止的原因是: {}'.format(MANTRA, error)
    else:
        message = '{}\n目前狀態{}'.format(MANTRA, status)

    return message


def isin_web(Flux):
    try:
        Flux.select_file('/SD/Recent/webUpload.fc')
        Flux.start_play()
        message = '{}\n開始印上次網頁上傳的檔案了～'.format(MANTRA)
    except:
        message = '{}\n無法開始，可能已經開始了\n或需要先停止任務喔'.format(MANTRA)
    return message


def isin_fs(Flux):
    try:
        Flux.select_file('/SD/Recent/recent-1.fc')
        Flux.start_play()
        message = '{}\n開始印上次FLUX STUDIO匯入的檔案了～'.format(MANTRA)
    except:
        message = '{}\n無法開始，可能已經開始了\n或需要先停止任務喔'.format(MANTRA)
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
        message = '{}\n已經繼續啟動了呢'.format(MANTRA)
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


@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload_file.html')

    if request.method == 'POST':
        if bool(request.files):
            if os.environ['passed'] != "True":
                return "Methods is not allowed."
            file = request.files['file']
            if file.filename == '':
                return "File cannot be empty."
            if file and allowed_file(file.filename, 'fc'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['FC_UPLOAD_FOLDER'],
                                         filename)
                file.save(file_path)
                try:
                    Flux = robot()
                except socket.timeout:
                    return 'FLUX connection temporarily not available.'
                Flux.upload_file(file_path, '/SD/Recent/webUpload.fc',
                                 process_callback=upload_callback)
                Flux.select_file('/SD/Recent/webUpload.fc')
                Flux.start_play()
                Flux.close()
                os.environ['passed'] = "False"
                return 'success'
            else:
                return "File type must is fc."

        elif bool(request.form):
            password = request.form['password']
            if password != os.environ['password']:
                return "password is different from FLUX's."
            os.environ['passed'] = "True"
            return 'passed'


@app.route("/callback", methods=['POST'])
def callback():
    if request.method == 'POST':
        js = request.get_json()
        _id, message, contentType = get_message(js)
        if _id != LINEID:
            message = '{0}\n請先在Heroku網頁新增{}的ID喔\n{}'.format(
                                                            MANTRA, NAME, _id)
            send_message(_id, message)
            return "ok"
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
            try:
                Flux = robot()
            except socket.timeout:
                message = '{}\n{}找不到FLUX喔～'.format(MANTRA, NAME)
                send_message(_id, message)
                return 'ok'

            if isin(message, status_set):
                message = isin_status(Flux)

            elif isin(message, list_files_set):
                message = isin_list_files(Flux)

            elif isin(message, start_set):
                message = '{}\n請指定要開始什麼喔～\n211 - web\n212 - fs'.format(MANTRA)

            elif isin(message, web_set):
                message = isin_web(Flux)

            elif isin(message, fs_set):
                message = isin_fs(Flux)

            elif isin(message, pause_set):
                message = isin_pause(Flux)

            elif isin(message, resume_set):
                message = isin_resume(Flux)

            elif isin(message, abort_set):
                message = isin_abort(Flux)

            else:
                message = '{}\n{}不知道"{}"是什麼啦！'.format(MANTRA, NAME, message[5:])

            send_message(_id, message)
            Flux.close()
            return 'ok'

        else:
            message = '{0}知道什麼是"{1}"，但是{0}不說'.format(NAME, message)
            send_message(_id, message)
            return 'ok'
