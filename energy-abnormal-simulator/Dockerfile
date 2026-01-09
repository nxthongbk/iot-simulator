# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /energy-abnormal-simulator

COPY requirements.txt requirements.txt

RUN apt-get update -y

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python","-u", "energy-abnormal-simulator.py"]