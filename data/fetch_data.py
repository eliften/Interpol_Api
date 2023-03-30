import io
import json
import os

import requests
from urllib.parse import urlparse, parse_qs
import logging

from dotenv import load_dotenv

from amqp_conns import amqp_connection
import pika
from apscheduler.schedulers.background import BackgroundScheduler


load_dotenv()

class RabbitMQ:
    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST')
        self.port = os.getenv('RABBITMQ_PORT')
        self.username = os.getenv('RABBITMQ_USERNAME')
        self.password = os.getenv('RABBITMQ_PASSWORD')
        self.virtual_host = os.getenv('RABBITMQ_VIRTUAL_HOST')
        self.queue_name = os.getenv('RABBITMQ_QUEUE_NAME')

    def connection(self):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.parameters = pika.ConnectionParameters(self.host,
                                                    self.port,
                                                    self.virtual_host,
                                                    self.credentials, heartbeat=50)

        self.connect = None
        self.channel = None

        if not self.connect or self.connect.is_closed:
            self.connect = pika.BlockingConnection(self.parameters)
            self.create_channel()

    def create_channel(self):
        self.channel = self.connect.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def send_message(self, message):
        try:
            self.connection()
            self.channel.basic_publish(exchange='',
                                       routing_key=self.queue_name,
                                       body=message)
        except pika.exceptions.AMQPError as p:
            self.connect.close()
            self.channel = None

def fetch():
    api_url = os.getenv("API_URL")
    start_page = 1
    try:
        interpol_response = requests.request("GET", api_url)
        if interpol_response.ok:
            data = interpol_response.json()
            total_page_url = data['_links']['last']['href']
            records = dict()
            records[start_page] = data['_embedded']['notices']
            parsed_url = urlparse(total_page_url)
            query_params = parse_qs(parsed_url.query)
            total_page_number = int(query_params['page'][0])
            for i in range(start_page, total_page_number + 1):
                new_page_response = requests.get(api_url + "&page=" + str(i))
                records[i] = new_page_response.json()
            record_data = json.dumps(records)
            records_js_data = json.loads(record_data)
            return records_js_data
    except Exception as e:
        logging.error(f'{e}')


def parse_data():
    obj = dict()
    main_obj = dict()
    records_data = fetch()
    for i in records_data:
        notices = (records_data[i]['_embedded']['notices'])
        for i in notices:
            detail_url = i['_links']['self']['href']
            detail_response = requests.get(detail_url)
            detail_record = detail_response.json()
            obj['forename'] = detail_record['forename']
            obj['name'] = detail_record['name']
            obj['date_of_birth'] = detail_record['date_of_birth']
            obj['place_of_birth'] = detail_record['place_of_birth']
            obj['entity_id'] = detail_record['entity_id']
            obj['nationalities'] = detail_record['nationalities']
            obj['languages_spoken_ids'] = detail_record['languages_spoken_ids']
            obj['height'] = detail_record['height']
            obj['sex_id'] = detail_record['sex_id']
            obj['eyes_colors_id'] = detail_record['eyes_colors_id']
            obj['hairs_id'] = detail_record['hairs_id']
            obj['distinguishing_marks'] = detail_record['distinguishing_marks']
            obj['issuing_country_id'] = detail_record['arrest_warrants'][0]['issuing_country_id']
            obj['charge'] = detail_record['arrest_warrants'][0]['charge']
            obj['charge_translation'] = detail_record['arrest_warrants'][0]['charge_translation']
            image_url = i['_links']['images']['href']
            image_response = requests.get(image_url)
            obj['image'] = io.BytesIO(image_response.content)
            main_obj[obj['entity_id']] = obj
    return main_obj

if __name__ == "__main__":
    client = RabbitMQ()
    scheduler = BackgroundScheduler()
    scheduler.start()

    interval = int(os.getenv("FETCH_INTERVAL_SECONDS"))

    job = scheduler.add_job(parse_data(), 'interval', minutes=interval)

    try:
        while True:
            tra = os.getenv("REAL_TIME_TRACKING")
            if tra != "true":
                logging.error("this connection not enable for tracking")
                break
            records = job.run()
            client.send_message(records)
            continue
    except KeyboardInterrupt:
        scheduler.shutdown()
