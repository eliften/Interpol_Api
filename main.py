import os
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv, set_key

import amqp_connection
import compare_data
import fetch_data

load_dotenv()

def run():
    db_status = os.getenv('IS_DB_CREATED')
    compare_data.listenQueueAndComparing.listenQueue()
    if db_status == "false":
        compare_data.listenQueueAndComparing.creatDB()
        set_key('IS_DB_CREATED', "true")
    compare_data.listenQueueAndComparing.creat_delta_db()

if __name__ == "__main__":
    client = amqp_connection.RabbitMQ()
    scheduler = BackgroundScheduler()
    scheduler.start()

    interval = int(os.getenv("FETCH_INTERVAL_SECONDS"))

    job = scheduler.add_job(fetch_data.parse_data(), 'interval', minutes=interval)

    try:
        while True:
            tra = os.getenv("REAL_TIME_TRACKING")
            if tra != "true":
                logging.error("this connection not enable for tracking")
                break
            job.run()
            continue
    except KeyboardInterrupt:
        scheduler.shutdown()
    compare_data.listenQueueAndComparing.compare()
