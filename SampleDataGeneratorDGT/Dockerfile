FROM python:3.11-slim

WORKDIR /SampleDataGeneratorARM

COPY ./SampleDataGeneratorARM/requirements.txt .
RUN pip install -r requirements.txt

COPY ./SampleDataGeneratorARM/sample.py /SampleDataGeneratorARM/sample.py

CMD ["python", "-u", "sample.py"]