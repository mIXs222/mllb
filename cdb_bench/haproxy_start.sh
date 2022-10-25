#!/bin/bash

if [ "$#" -ne 1 ]
then
  echo "Require 1 argument(s) (HAPROXY_DOCKER_IMAGE), $# provided"
  exit 1
fi

# Official image: haproxytech/haproxy-alpine:2.4
# Dev image: haprox-2.4-alpine-dev
HAPROXY_DOCKER_IMAGE=$1
echo "Starting HAProxy from ${HAPROXY_DOCKER_IMAGE}"

echo "Generating HAProxy configuration at haproxy.cfg"
docker exec -it roach1 ./cockroach gen haproxy --certs-dir=certs --host=roach1 --port=26257 --insecure
docker cp roach1:/cockroach/haproxy.cfg haproxy.cfg

docker run -d --name haproxy --net roachnet -v $(pwd):/usr/local/etc/haproxy:ro -p 26257:26257 -p 8404:8404 ${HAPROXY_DOCKER_IMAGE}
