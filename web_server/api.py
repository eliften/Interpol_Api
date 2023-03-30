import os

from dotenv import set_key
from flask import Flask, render_template, request
import sqlite3

from web_server import compare_data

app = Flask(__name__)


@app.route('/', methods=['POST'])
def allRecords():
    conn = sqlite3.connect('interpol.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM red_list')
    data = cursor.fetchall()
    return render_template('index.html', data=data)


@app.route('/deleted_alert', methods=['POST'])
def delete_alert():
    raw_data = request.json
    data = raw_data['deleted_data']
    return render_template('index.html', data=data)


@app.route('/added_alert', methods=['POST'])
def added_alert():
    raw_data = request.json
    data = raw_data['added_data']
    return render_template('index.html', data=data)

if __name__ == "__main__":
    db_status = os.getenv('IS_DB_CREATED')
    compare_data.listenQueueAndComparing.listenQueue()
    if db_status == "false":
        compare_data.listenQueueAndComparing.creatDB()
        set_key('IS_DB_CREATED', "true")
    compare_data.listenQueueAndComparing.creat_delta_db()
    app.run()