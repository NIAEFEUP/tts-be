# deps
FROM python:3.8-slim-buster AS deps

WORKDIR /usr/src/django/

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt ./requirements.txt

RUN apt-get update
RUN apt-get -y install build-essential
RUN apt-get -y install protobuf-compiler

COPY ../tts-protobufs/protos/ ./tts-protobufs/protos/

RUN mkdir -p ./generated

RUN protoc --python_out=./generated ./tts-protobufs/protos/

COPY ./etc/pgdg.sh /tmp/pgdg.sh
RUN /tmp/pgdg.sh

RUN apt -y install libpq-dev postgresql-client-16
RUN apt -y clean && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

EXPOSE 8000

COPY ./entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["/usr/src/django/entrypoint.sh"]

# prod
FROM deps AS prod

COPY tts_be/ ./tts_be
COPY university/ ./university
COPY manage.py tasks.py ./

COPY ./entrypoint_prod.sh ./entrypoint_prod.sh
ENTRYPOINT ["/usr/src/django/entrypoint_prod.sh"]