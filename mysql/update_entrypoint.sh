#!bin/sh

cat  sql/db_creation.sql > entrypoint.sql
for FILE in sql/populate/*; do
    cat $FILE >> entrypoint.sql;
done 

