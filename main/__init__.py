from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cx_Oracle
import sys
import os

try:
    lib_dir=r"C:\oracle\instantclient_21_3"
    cx_Oracle.init_oracle_client(lib_dir=lib_dir)
except Exception as err:
    print("Whoops!")
    print(err)
    sys.exit(1)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "123456")

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = '請登入'
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
#  很重要，一定要放這邊
from main import views