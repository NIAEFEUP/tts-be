FROM postgres:16-alpine

ENV LANG=C.UTF-8
ADD ./sql/*.sql docker-entrypoint-initdb.d/
