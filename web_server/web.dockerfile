FROM python:3.9-slim-buster

WORKDIR /web_server

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY /web_service .

EXPOSE 8001

CMD ["/usr/local/bin/python3", "api.py"]