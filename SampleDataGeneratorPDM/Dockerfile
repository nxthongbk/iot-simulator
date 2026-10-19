FROM python:3.11-slim

WORKDIR /SampleDataGeneratorPDM
COPY requirements.txt requirements.txt


RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-u", "sample.py"]