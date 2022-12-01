#!/bin/bash

if [ "$#" -ne 3 ]
then
  echo "Require 3 argument(s) (HAPROXY_DOCKER_IMAGE, HAPROXY_CONFIG, NUM_SERVERS), $# provided"
  exit 1
fi
HAPROXY_DOCKER_IMAGE=$1
HAPROXY_CONFIG=$2
NUM_SERVERS=$3

echo ">>> simple_start"
bash simple_bench/simple_start.sh ${NUM_SERVERS}

echo ">>> haproxy_start"
bash simple_bench/haproxy_start.sh ${HAPROXY_DOCKER_IMAGE}  ${HAPROXY_CONFIG}

echo ">>> ab"
ab -n 10000 -c 32 127.0.0.1:8080/

echo ">>> haproxy_stop"
bash simple_bench/haproxy_stop.sh

echo ">>> simple_stop"
bash simple_bench/simple_stop.sh ${NUM_SERVERS}