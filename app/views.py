from flask import render_template, request, jsonify
from app import app

@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('main.html')

