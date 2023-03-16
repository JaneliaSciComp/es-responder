#!/bin/sh

docker-compose -f docker-compose-dev.yml down
docker container ls -a | grep es-responder-app | awk '{print $1}' | xargs docker container rm
docker image ls | grep es-responder-app | awk '{print $3}' | xargs docker image rm
docker volume rm es-responder_static_volume
#docker pull registry.int.janelia.org/jacs/configurator:latest
docker-compose -f docker-compose-dev.yml up
