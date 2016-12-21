import os
# import mimetypes
from flask import Flask
# from flask.ext.login import LoginManager
# from flask.ext.sqlalchemy import SQLAlchemy

# mimetypes.add_type('image/svg+xml', '.svg'# )

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'blesscat-Web-Console-SecretKey'

app.config['FC_UPLOAD_FOLDER'] = basedir
app.config['FC_ALLOWED_EXTENSIONS'] = set(['fc'])

# app.debug = True

# ===================LoginManager=====================================================
# login_manager = LoginManager()
# login_manager.init_app(app)

# ===================SQLAlchemy=======================================================
# track_modifications = app.config.setdefault(
#    'SQLALCHEMY_TRACK_MODIFICATIONS', True)
# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/app.db'
# db = SQLAlchemy(app)

from app import views, watchcat
