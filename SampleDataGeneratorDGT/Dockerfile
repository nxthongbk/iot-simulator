FROM python:3.11-slim

WORKDIR /SampleDataGeneratorDGT

COPY ./SampleDataGeneratorDGT/requirements.txt .
RUN pip install -r requirements.txt

COPY ./SampleDataGeneratorDGT/sample.py /SampleDataGeneratorDGT/sample.py

CMD ["python", "-u", "sample.py"]