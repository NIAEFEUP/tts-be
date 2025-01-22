# deps
FROM python:3.11-slim AS deps

WORKDIR /usr/src/django/

# Get's the output from the django in realtime.
ENV PYTHONUNBUFFERED=1

# Copy requirements
COPY ./django/requirements.txt ./requirements.txt

COPY ./tts-protobufs protos  

# Dependencies for building the requirements
RUN apt-get update
RUN apt-get -y install build-essential protobuf-compiler git

RUN git init
RUN git submodule init
RUN git submodule update

# Install postgres dependencies (pgsql client and development files)
COPY ./django/etc/pgdg.sh /tmp/pgdg.sh
RUN /tmp/pgdg.sh

RUN apt -y install libpq-dev postgresql-client-16
RUN apt -y clean && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

EXPOSE 8000

# Install the requirements
COPY ./django/entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["/usr/src/django/entrypoint.sh"]

# prod
FROM deps AS prod

COPY django/tts_be/ ./tts_be
COPY django/university/ ./university
COPY django/manage.py django/tasks.py ./

COPY ./django/entrypoint_prod.sh ./entrypoint_prod.sh
ENTRYPOINT ["/usr/src/django/entrypoint_prod.sh"]