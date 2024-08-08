FROM python:3.8-slim-buster

WORKDIR /usr/src/django/ 

# Get's the output from the django in realtime. 
ENV PYTHONUNBUFFERED 1

# Copy requirements 
COPY ./requirements.txt ./requirements.txt 

# Dependencies for mysqlclient 
RUN apt-get update
RUN apt-get -y install build-essential default-libmysqlclient-dev

# Install mysql command to wait for the database initialization 
RUN apt -y install default-mysql-client

# Install the requirements
RUN pip install -r requirements.txt

EXPOSE 8000

COPY ./entrypoint.sh ./entrypoint.sh  
ENTRYPOINT ["sh", "/usr/src/django/entrypoint.sh"]
