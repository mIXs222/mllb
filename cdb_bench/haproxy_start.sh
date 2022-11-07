#!/bin/bash

if [ "$#" -ne 2 ]
then
  echo "Require 2 argument(s) (HAPROXY_DOCKER_IMAGE, HAPROXY_CONFIG), $# provided"
  exit 1
fi
HAPROXY_DOCKER_IMAGE=$1
HAPROXY_CONFIG=$2
echo "Using HAPROXY_DOCKER_IMAGE= ${HAPROXY_DOCKER_IMAGE}, HAPROXY_CONFIG= ${HAPROXY_CONFIG}"

# Official image: haproxytech/haproxy-alpine:2.4
# Dev image: haprox-2.4-alpine-dev
echo "Starting HAProxy from ${HAPROXY_DOCKER_IMAGE}"

# Special config file(s)
if [ ${HAPROXY_CONFIG} == "roach" ]
then
  echo "Generating HAProxy configuration at haproxy_roach.cfg"
  docker exec -it roach1 ./cockroach gen haproxy --certs-dir=certs --host=roach1 --port=26257 --insecure
  docker cp roach1:/cockroach/haproxy.cfg haproxy_roach.cfg
  HAPROXY_CONFIG=haproxy_roach.cfg
fi
cp ${HAPROXY_CONFIG} haproxy.cfg

# Confirm config file
cat ${HAPROXY_CONFIG}
echo "From configuration file at ${HAPROXY_CONFIG}"

docker run -d --name haproxy --net roachnet -v $(pwd):/usr/local/etc/haproxy:ro -p 26257:26257 -p 8404:8404 ${HAPROXY_DOCKER_IMAGE}
