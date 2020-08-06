from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_restplus import Api
import os

# app
app = Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://lukaiyi:Z5lsw@123456#@39.104.91.14:3306/telecom_field_control'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'be9a5f1a92ac4bc2b0d8e1a5b315600d'  # csrf
app.config['JSON_AS_ASCII'] = False


db = SQLAlchemy(app)
pymysql.install_as_MySQLdb()



from process_control.admin import admin as admin_blueprint
from process_control.admin_interface import admin_interface as admin_interface_blueprint

# 注册蓝图
app.register_blueprint(admin_blueprint)
app.register_blueprint(admin_interface_blueprint, url_prefix='/api')

@app.errorhandler(404)
def page_not_find(err):
    return render_template('admin/404.html'), 404