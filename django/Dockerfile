FROM python:3.8-slim-buster

WORKDIR /usr/src/django/ 

# Get's the output from the django in realtime. 
ENV PYTHONUNBUFFERED 1

# Copy requirements 
COPY ./requirements.txt ./requirements.txt 

# Dependencies for building the requirements
RUN apt-get update
RUN apt-get -y install build-essential

# Install postgres dependencies (pgsql client and development files)

# https://www.postgresql.org/download/linux/ubuntu/
COPY ./etc/pgdg.sh /tmp/pgdg.sh
RUN /tmp/pgdg.sh

RUN apt -y install libpq-dev postgresql-client-16

# Install the requirements
RUN pip install -r requirements.txt

EXPOSE 8000

COPY ./entrypoint.sh ./entrypoint.sh  
ENTRYPOINT ["/usr/src/django/entrypoint.sh"]
