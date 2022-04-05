#coding=utf-8  
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cx_Oracle
import sys
import os
from dotenv import load_dotenv
load_dotenv()

#### LINUX env use 
#### export LD_LIBRARY_PATH=/home/ubuntu/docker_lab/equip_ms/instantclient_ubuntu:$LD_LIBRARY_PATH
#### source ~/.bashrc 
try:
    if sys.platform.startswith("linux"):
        cx_Oracle.init_oracle_client()
    elif sys.platform.startswith("win32"):
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

# app.config['SQLALCHEMY_DATABASE_URI'] = "oracle://GROUP5:group5group5@140.117.69.58:1521/orcl"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
connection = cx_Oracle.connect(os.getenv("DB_USERNAME"), os.getenv("DB_PASSWORD"), cx_Oracle.makedsn(os.getenv("DB_HOST"), 1521, os.getenv("DB_NAME"))) # 連線資訊
cursor = connection.cursor()
#  很重要，一定要放這邊
from main import views