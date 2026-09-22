FROM python:3.11-slim

WORKDIR /SampleDataGeneratorDGT

COPY ./SampleDataGeneratorDGT/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-u", "sample.py"]