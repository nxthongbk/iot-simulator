# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /DEV-261030-000000030

COPY requirements.txt requirements.txt

RUN apt-get update -y

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python","-u", "DEV-261030-000000030.py"]