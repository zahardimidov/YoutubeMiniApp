FROM python:3.10-alpine

RUN apk add --no-cache ffmpeg

WORKDIR /downloader

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD python run.py