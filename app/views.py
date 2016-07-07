from flask import render_template, request, jsonify
from app import app


@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('main.html')


@app.route("/callback", methods=['POST'])
def callback():
    if request.method == 'POST':
        print(request.get_json())
        return 'test'
