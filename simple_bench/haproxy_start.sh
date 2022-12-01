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

# Confirm config file
cp ${HAPROXY_CONFIG} haproxy.cfg
cat ${HAPROXY_CONFIG}
echo "From configuration file at ${HAPROXY_CONFIG}"

docker run -d --name haproxy --net roachnet -v $(pwd):/usr/local/etc/haproxy:ro -p 8085:8080 ${HAPROXY_DOCKER_IMAGE}
