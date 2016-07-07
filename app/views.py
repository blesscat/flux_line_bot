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
        js = request.get_json()
        print(type(js))
        print(len(js['result']))
        return 'test'
