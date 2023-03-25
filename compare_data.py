import os
import requests

import amqp_connection
import sqlite3
from queue import Queue
import json
from datetime import datetime


class listenQueueAndComparing:
    def __init__(self):
        self.channel = amqp_connection.RabbitMQ.run_listen()
        self.queue = Queue

    def listenQueue(self):
        queue_name = os.getenv('RABBITMQ_QUEUE_NAME')
        self.channel.basic_consume(queue_name, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        self.queue.put(json.loads(body))

    def creatDB(self):
        body = self.queue.get()
        conn = sqlite3.connect('interpol.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS red_list
                        (forename TEXT,
                        name TEXT,
                        date_of_birth TEXT,
                        place_of_birth TEXT,
                        entity_id TEXT,
                        nationalities TEXT,
                        height TEXT,
                        sex_id TEXT,
                        eyes_colors_id TEXT,
                        hairs_id TEXT,
                        distinguishing_marks TEXT,
                        issuing_country_id TEXT,
                        charge TEXT,
                        charge_translation TEXT,
                        image TEXT
                        datetime TEXT''')
        cursor.execute('INSERT INTO red_list (forename, name, date_of_birth, place_of_birth, entity_id, nationalities, height, sex_id, eyes_colors_id, hairs_id, distinguishing_marks, issuing_country_id, charge, charge_translation, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (body[0], body[1], body[2], body[3], body[4], body[5], body[6], body[7], body[8], body[10], body[11], body[12], body[13], body[14], datetime.now()))
        conn.commit()

    def creat_delta_db(self):
        body = self.queue.get()
        conn = sqlite3.connect('interpol.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS delta
                        (forename TEXT,
                        name TEXT,
                        date_of_birth TEXT,
                        place_of_birth TEXT,
                        entity_id TEXT,
                        nationalities TEXT,
                        height TEXT,
                        sex_id TEXT,
                        eyes_colors_id TEXT,
                        hairs_id TEXT,
                        distinguishing_marks TEXT,
                        issuing_country_id TEXT,
                        charge TEXT,
                        charge_translation TEXT,
                        image TEXT
                        datetime TEXT''')
        cursor.execute('INSERT INTO delta (forename, name, date_of_birth, place_of_birth, entity_id, nationalities, height, sex_id, eyes_colors_id, hairs_id, distinguishing_marks, issuing_country_id, charge, charge_translation, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (body[0], body[1], body[2], body[3], body[4], body[5], body[6], body[7], body[8], body[10], body[11], body[12], body[13], body[14], datetime.now()))
        conn.commit()

    def compare(self):
        conn = sqlite3.connect('interpol.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM red_list")

        cursor.execute("SELECT * FROM delta")

        deleted_result = cursor.execute(
            "SELECT red_list.* FROM red_list LEFT JOIN delta ON red_list.entity_id = delta.entity_id WHERE delta.entity_id IS NULL")

        added_result = cursor.execute(
            "SELECT delta.* FROM delta LEFT JOIN red_list ON delta.entity_id = red_list.entity_id WHERE red_list.entity_id IS NULL")

        added_data = [dict(zip(row.keys(), row)) for row in added_result]
        deleted_data = [dict(zip(row.keys(), row)) for row in deleted_result]

        requests.post('http://127.0.0.1:5000/deleted_alert', json={'deleted_data': deleted_data})
        requests.post('http://127.0.0.1:5000/added_alert', json={'added_data': added_data})

        cursor.execute('SELECT * FROM delta')
        data = cursor.fetchall()
        cursor.executemany('INSERT INTO red_list VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
        conn.commit()

        conn.close()


