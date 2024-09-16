# deps
FROM python:3.8-slim-buster AS deps

WORKDIR /usr/src/django/

# Get's the output from the django in realtime.
ENV PYTHONUNBUFFERED=1

# Copy requirements
COPY ./requirements.txt ./requirements.txt

# Dependencies for building the requirements
RUN apt-get update
RUN apt-get -y install build-essential
RUN apt-get -y install protobuf-compiler

# Generating the python files from the protobufs
COPY ./tts-protobufs/protos/ ./protos
RUN mkdir -p ./generated
RUN protoc --python_out=./generated ./protos

# Install postgres dependencies (pgsql client and development files)
COPY ./etc/pgdg.sh /tmp/pgdg.sh
RUN /tmp/pgdg.sh

RUN apt -y install libpq-dev postgresql-client-16
RUN apt -y clean && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

EXPOSE 8000

# Install the requirements
COPY ./entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["/usr/src/django/entrypoint.sh"]

# prod
FROM deps AS prod

COPY tts_be/ ./tts_be
COPY university/ ./university
COPY manage.py tasks.py ./

COPY ./entrypoint_prod.sh ./entrypoint_prod.sh
ENTRYPOINT ["/usr/src/django/entrypoint_prod.sh"]