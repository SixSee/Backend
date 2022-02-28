FROM python:3.10.1-alpine

RUN mkdir /backend
WORKDIR /backend

# Set Environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=.
RUN apk update && apk upgrade
RUN apk add --no-cache gcc \
 openssl-dev \
 musl-dev \
 mariadb-dev \
 && rm -rf /var/cache/apk/*
RUN apk add make cmake

# install dependencies
RUN python -m pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY ./ .

ENTRYPOINT python manage.py runserver 0.0.0.0:8000