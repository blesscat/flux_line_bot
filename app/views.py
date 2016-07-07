from flask import render_template, request, jsonify
import requests
from app import app


@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('main.html')


@app.route("/callback", methods=['POST'])
def callback():
    if request.method == 'POST':
        url = 'https://trialbot-api.line.me/v1/events'
        headers = {
                   'Content-Type': 'application/json; charset=UTF-8',
                   'X-Line-ChannelID': '1473077665',
                   'X-Line-ChannelSecret': '8582629c37b18605491087172be06e5e',
                   'X-Line-Trusted-User-With-ACL': 'u3425f8daf2f07f3a9d723f5232f50f63'
                  }
        data = {
                'to': ['u96e32e17ebdedd21c1f84bbbfd7de08c'],
                'toChannel': 1383378250,
                'eventType': '138311608800106203',
                'content': {
                    'contentType': 1,
                    'toType': 1,
                    'text': u'寶寶不說'
                    }
               }
        js = request.get_json()
        print(type(js))
        print(len(js['result']))

	r = requests.post(url, data=json.dumps(data), headers=headers)
	return json.dumps(r.json(), indent=4)
