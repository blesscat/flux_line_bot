# -*- coding: utf8 -*-
import os
import sys
import socket
import math
import time
import threading
import requests
import json
from flask import request, abort
from flask import render_template
from werkzeug import secure_filename
from app import app
from app.utils import count_words_at_url, assistant
from rq import Queue
from rq.job import Job

from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

sys.path.insert(0, os.path.abspath('..'))

from worker import conn
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

watchdogOn_set = {'131',
                'watchdogon'}

watchdogOff_set = {'132',
                'watchdogoff'}

watchdog_set = {'130',
                'watchdog'}

web_set = {'211',
           'startweb',
           'STARTWEB'}

fs_set = {'212',
          'startfs',
          'STARTFS'}

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
             '停止'}

quit_set = {'250',
            'quit',
            'QUIT',
            '終止',
            '結束'}

load_filament_set = {'260'}

unload_filament_set = {'261'}

FLUX_COMMANDS = ""
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


for command in flux_command_list:
    FLUX_COMMANDS += command + '\n'

fb_token = 'blesscat'
FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
MANTRA = os.environ['mantra']
NAME = os.environ['name']
LINEID = os.environ.get('LineID', 'test')
#os.environ['passed'] = "False"
ChannelAccessToken = os.environ.get('ChannelAccessToken')
ChannelSecret = os.environ.get('ChannelSecret')

line_bot_api = LineBotApi(ChannelAccessToken)
handler = WebhookHandler(ChannelSecret)
#parser = WebhookParser(ChannelSecret)
q = Queue(connection=conn)

lang_file = 'zh_tw.json'
lang_dir_path = os.path.join(app.static_folder, 'lang')

with open(os.path.join(lang_dir_path, lang_file)) as f:
    LANG = json.load(f)


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
    FLUX_ipaddr = socket.gethostbyname(os.environ['FLUX_ipaddr'])
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


def add_rsa():
    Flux = FLUX((FLUX_ipaddr, 1901))
    result = Flux.add_rsa()
    return result


def isin_status(Flux):
    report = Flux.report_play()
    status = report['st_label']
    error = report.get('error', '[]')
    if status == 'RUNNING':
        label, prog, error, leftTime = get_flux_status(Flux)
        message = '{}\n目前狀態: {}\n目前進度: {}\n剩餘時間: {}'.format(
                   MANTRA, label, prog, leftTime)
    elif status == 'IDLE':
        #message = '{}\nFLUX目前閒置中喔'.format(MANTRA)
        message = LANG['status']['IDLE'].format(MANTRA)
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


def poke_watchdog_status():
    loop = 4
    for i in range(loop):
        try:
            time.sleep(0.5)
            dog_status = app.config['DOG'].isAlive()
            if dog_status:
                break
        except KeyError:
            web = os.environ['WEB_URL'] + '/dog_status'
            json = {'password': os.environ['password']}
            r = requests.post(web, json=json)
            if r._content != b'None':
                dog_status = True if r._content == b'True' else False
                break
            if i == loop-1:
                dog_status = False
    return dog_status

def isin_watchdogOn(Flux):
    dog_status = poke_watchdog_status()
    if dog_status:
        message = '{}\n{}已經在監測FLUX了!'.format(MANTRA, NAME)
    else:
   #     app.config['DOG'] = watchdog.watchdog()
        app.config['DOG'].start()
        message = '{}\n{}開始監測FLUX工作了!'.format(MANTRA, NAME)
    return message


def isin_watchdogOff(Flux):
    dog_status = poke_watchdog_status()
    if dog_status:
        try:
            app.config['DOG'].monitor = False
            del app.config['DOG']
        except:
            web = os.environ['WEB_URL'] + '/dogoff'
            json = {'password': os.environ['password']}
            r = requests.post(web, json=json)
            if r._content == b'None':
                return 'please try again'

        message = '{}\n{}不再監測FLUX工作了...呼～'.format(MANTRA, NAME)
    else:
        message = '{}\n{}並沒有在監測FLUX喔'.format(MANTRA, NAME)
    return message


def isin_watchdog(Flux):
    dog_status = poke_watchdog_status()
    if dog_status:
        message = '{}\n{}正在監測FLUX喔'.format(MANTRA, NAME)
    else:
        message = '{}\n{}並沒有在監測FLUX喔'.format(MANTRA, NAME)
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
        loop = 20
        Flux.resume_play()
        for i in range(loop):
            time.sleep(1)
            if Flux.report_play()['st_label'] == 'RUNNING':
                message = '{}\n已經繼續啟動了呢'.format(MANTRA)
                break
            else:
                if i == loop-1:
                    raise OSError
    except:
        message = '{}\n無法繼續，可能已經停止了\n或者請確認機台狀態喔'.format(MANTRA)
    return message


def isin_abort(Flux):
    try:
        Flux.abort_play()
        message = '{}\n已經停止囉'.format(MANTRA)
    except:
        message = '{}\n無法停止，可能早就已經停止了呢'.format(MANTRA)
    return message


def isin_quit(Flux):
    try:
        Flux.kick()
        message = '{}\n已經終止任務囉'.format(MANTRA)
    except:
        message = '{}\n無法終止，可能早就已經終止了呢'.format(MANTRA)
    return message


#def isin_load_filament(Flux):
#    maintain = backend.load_filament_backend(Flux)
#    maintain.start()
#
#def isin_unload_filament(Flux):
#    maintain = backend.unload_filament_backend(Flux)
#    maintain.start()

def isin_list_files(Flux):
    _list = str(Flux.list_files('/SD'))
    message = '{}'.format(_list)
    return message


@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        return 'main'

@app.route("/test", methods=['GET'])
def test():
    conn.set('abc',123)
    #job = q.enqueue_call(
    #                     func=count_words_at_url,
    #                     args=('http://heroku.com',),
    #                     job_id='test')
    #print(job.get_id())
    return 'ok', 200


@app.route("/test1", methods=['GET'])
def test1():
    result = conn.get('abc')
    #conn.save()
    print('{} ,{}'.format(result, type(result)))
    return 'ok', 200


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202


@app.route("/dog_status", methods=['POST'])
def dog_status():
    if request.method == 'POST':
        if request.json['password'] == os.environ['password']:
            try:
                result = app.config['DOG'].isAlive()
            except KeyError:
                result = None
            return str(result)


@app.route("/dogoff", methods=['POST'])
def dogoff():
    if request.method == 'POST':
        if request.json['password'] == os.environ['password']:
            try:
                app.config['DOG'].monitor = False
                del app.config['DOG']
                result = 'ok'
            except KeyError:
                result = None
            return str(result)


@app.route("/thread", methods=['GET'])
def thread():
    if request.method == 'GET':
        result = threading.activeCount()
        return str(result)


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
                except:
                    return 'FLUX connection temporarily not available.'
                Flux.upload_file(file_path, '/SD/Recent/webUpload.fc',
                                 process_callback=upload_callback)
                Flux.select_file('/SD/Recent/webUpload.fc')
                Flux.start_play()
                Flux.close()
                os.environ['passed'] = "False"
                while os.environ['passed'] != "False":
                    time.sleep(0.1)
                return 'success'
            else:
                return "File type must is fc."

        elif bool(request.form):
            password = request.form['password']
            if password != os.environ['password']:
                return "password is different from FLUX's."
            os.environ['passed'] = "True"
            while os.environ['passed'] != "True":
                time.sleep(0.1)
            return 'passed'


@app.route("/fb_callback", methods=['GET', 'POST'])
def fb_callback():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        if verify_token == fb_token:
            return request.args.get('hub.challenge')
        return 'fail'
    if request.method == 'POST':
        data = request.get_json()
        print(data)

        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    if messaging_event.get("message"):  # someone sent us a message
                        sender_id = messaging_event["sender"]["id"]
                        #recipient_id = messaging_event["recipient"]["id"]
                        message_text = messaging_event["message"]["text"]
                        params = {
                        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
                        }
                        headers = {
                            "Content-Type": "application/json"
                        }
                        data = json.dumps({
                            "recipient": {
                                "id": sender_id
                            },
                            "message": {
                                "text": message_text
                            }
                        })
                        print('data: {}'.format(data))
                        r = requests.post("https://graph.facebook.com/v2.6/me/messages",params=params, headers=headers, data=data)
                        if r.status_code != 200:
                            print(r.status_code)
                            print(r.text)


                    if messaging_event.get("delivery"):  # delivery confirmation
                        pass
                    if messaging_event.get("optin"):  # optin confirmation
                        pass
                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                        pass
        return 'ok', 200           
    

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    _id = event.source.sender_id
    message = event.message.text
    assist = assistant(_id, message)
    print(dir(assist.name))

    if _id != assist.LINEID:
        message = '{}\n請先在Heroku網頁新增{}的LineID喔\n\n{}'.format(
                                                    MANTRA, NAME, _id)
        line_bot_api.reply_message( event.reply_token, TextSendMessage(text=message))
        return "ok"

    if message == '罐罐':
        message = '{0}要吃罐罐！！\n{0}要吃罐罐！！\n給{0}吃！！'.format(NAME)
        line_bot_api.reply_message( event.reply_token, TextSendMessage(text=message))
        time.sleep(5)
        message = '{}\n{}能做的工作如下喔!\n{}'.format(MANTRA, NAME, FLUX_COMMANDS)
        line_bot_api.push_message(_id, TextSendMessage(text=message))
        return 'ok'

    magic_id = message[:5].lower()
    if magic_id == 'flux ' or magic_id == '8763 ':
        try:
            Flux = robot()
        except:
            message = '{}\n{}找不到FLUX喔～'.format(MANTRA, NAME)
            line_bot_api.reply_message( event.reply_token, TextSendMessage(text=message))
            return 'ok'

        if isin(message, watchdogOn_set):
            message = isin_watchdogOn(Flux)

        elif isin(message, watchdogOff_set):
            message = isin_watchdogOff(Flux)

        elif isin(message, watchdog_set):
            message = isin_watchdog(Flux)

        elif isin(message, status_set):
            message = isin_status(Flux)

        elif isin(message, list_files_set):
            message = isin_list_files(Flux)

        elif isin(message, web_set):
            message = isin_web(Flux)

        elif isin(message, fs_set):
            message = isin_fs(Flux)

        elif isin(message, start_set):
            message = '{}\n請指定要開始什麼喔～\n211 - web\n212 - fs'.format(MANTRA)

        elif isin(message, pause_set):
            message = isin_pause(Flux)

        elif isin(message, resume_set):
            message = isin_resume(Flux)

        elif isin(message, abort_set):
            message = isin_abort(Flux)

        elif isin(message, quit_set):
            message = isin_quit(Flux)

#        elif isin(message, load_filament_set):
#            message = isin_load_filament(Flux)
#
#        elif isin(message, unload_filament_set):
#            message = isin_unload_filament(Flux)

        else:
            message = '{}\n{}不知道"{}"是什麼啦！'.format(MANTRA, NAME, message[5:])

        line_bot_api.reply_message( event.reply_token, TextSendMessage(text=message))
        Flux.close()
        return 'ok'

    else:
        #message = '{0}知道什麼是"{1}"，但是{0}不說'.format(NAME, message)
        message = LANG['illegal_comm'].format(assist=assist)
        print(message)
        line_bot_api.reply_message( event.reply_token, TextSendMessage(text=message))
        return 'ok'
