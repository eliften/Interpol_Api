import os
import pika
import json


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

    def run_listen(self):
        self.connection()
        return self.channel

