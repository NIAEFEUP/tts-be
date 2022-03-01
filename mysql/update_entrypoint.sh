#!bin/sh

for FILE in sql/*; do
    cat $FILE >> entrypoint.sql;
done 

