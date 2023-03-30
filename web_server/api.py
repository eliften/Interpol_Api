import os

from dotenv import set_key
from flask import Flask, render_template, request
import sqlite3

from web_server import compare_data

app = Flask(__name__)


@app.route('/', methods=['POST'])
def allRecords(): # publish all database
    conn = sqlite3.connect('interpol.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM red_list')
    data = cursor.fetchall()
    return render_template('index.html', data=data)


@app.route('/deleted_alert', methods=['POST'])
def delete_alert(): # publish detected deleted data
    raw_data = request.json
    data = raw_data['deleted_data']
    data['Update_Type'] = 'deleted_data'
    return render_template('update_index.html', data=data)


@app.route('/added_alert', methods=['POST'])
def added_alert(): # publish added deleted data
    raw_data = request.json
    data = raw_data['added_data']
    data['Update_Type'] = 'added_data'
    return render_template('update_index.html', data=data)

if __name__ == "__main__":
    db_status = os.getenv('IS_DB_CREATED')
    compare_data.listenQueueAndComparing.listenQueue()
    if db_status == "false": #run without compare if the project is running for the first time
        compare_data.listenQueueAndComparing.creatDB()
        set_key('IS_DB_CREATED', "true")
    compare_data.listenQueueAndComparing.creat_delta_db()
    app.run()