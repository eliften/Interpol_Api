from flask import Flask, render_template, request
import sqlite3

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


app.run()
