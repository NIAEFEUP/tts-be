#!/usr/bin/env bash 

if [ -f "./mysql/data/" ] ; then
    sudo rm -rf "./mysql/data/"
    echo ">> ./mysql/data/ deleted with success" 
fi

DOCKER_NETWORKS=$(docker network ls)
TTS_NETWORK=$(echo $DOCKER_NETWORKS | grep 'tts_bridge ')
if [ -z "$TTS_NETWORK" ]
then 
    echo ">> Missing tts_bridge network. Creating..."
    docker network create 'tts_bridge'
else 
    echo ">> Detected tts_bridge network!"
fi

echo ">> Formating ./django/entrypoint.sh file"
sed -i 's/\r$//' ./django/entrypoint.sh   

echo ">> Removing old containers..."
docker-compose down 
echo ">> Initializing docker..."
docker-compose up --build