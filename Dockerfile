FROM python:3.13-alpine

RUN pip install --no-cache-dir kataloger

WORKDIR /project

ENTRYPOINT ["kataloger"]
