FROM python:3.9

WORKDIR /amqp_conns

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "amqp_connection.py"]