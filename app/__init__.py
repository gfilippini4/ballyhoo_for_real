# Welcome to the Flask-Bootstrap sample application. This will give you a
# guided tour around creating an application using Flask-Bootstrap.
#
# To run this application yourself, please install its requirements first:
#
#   $ pip install -r sample_app/requirements.txt
#
# Then, you can actually run the application.
#
#   $ flask --app=sample_app dev
#
# Afterwards, point your browser to http://localhost:5000, then check out the
# source.

from flask import Flask, url_for, render_template, request, jsonify
from flask_bootstrap import Bootstrap
import json
import mysql.connector as connector
client = connector.connect(user='ballyhoo',password='[newsnow]',host='127.0.0.1',database='Articles')
cursor = client.cursor()

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('base_extended.html')

@app.route("/getHooks", methods=['GET', 'POST'])
def get_hooks():
    if request.method =='POST':
        data = request.get_json()
        print(data)
        dict =  hit_database(data['hooks'].split())
        return jsonify(dict)

@app.route("/getAllHooks", methods=['GET','POST'])
def get_all_hooks():
    if request.method =='POST':
        data = {'hooks': []}
        sql = "select distinct(hook) from Articles.hooks;"
        cursor.execute(sql)
        for hook in cursor:
            data['hooks'].append(hook)
        return jsonify(data)

def hit_database(hooks):
    data = {}
    print(hooks)
    for hook in hooks:
        print(hook)
        try:
            cursor.execute("""
            select a.url, a.title from Articles.articles as a join Articles.hooks as h on a.id = h.id where h.hook = '""" + hook + "';")
            for url in cursor:
                if hook in data.keys():
                    data[hook].append(url)
                else:
                    data[hook] = [url]
            client.commit()
        except Exception as e:
            print(str(e))
    print(data)
    return data
