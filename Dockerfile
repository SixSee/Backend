FROM python:3.10.1-alpine

RUN mkdir /backend
WORKDIR /backend

# Set Environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=.
RUN apk update && apk upgrade
RUN apk --update add postgresql-client
RUN apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN python -m pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Copy project
COPY ./ .

ENTRYPOINT python manage.py runserver 0.0.0.0:8000
