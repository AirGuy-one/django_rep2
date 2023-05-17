FROM python:3.9-alpine3.18

RUN apk add postgresql-client

COPY requirements.txt /code/requirements.txt
COPY . /code/

WORKDIR /code

EXPOSE 8000

RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt
