#!/bin/bash

if [ "$#" -ne 4 ]
then
  echo "Require 4 argument(s) (HAPROXY_DOCKER_IMAGE, HAPROXY_CONFIG, NUM_SERVERS, CONCURRENCY), $# provided"
  exit 1
fi
HAPROXY_DOCKER_IMAGE=$1
HAPROXY_CONFIG=$2
NUM_SERVERS=$3
CONCURRENCY=$4

echo ">>> simple_start"
bash simple_bench/simple_start.sh ${NUM_SERVERS}

echo ">>> haproxy_start"
bash simple_bench/haproxy_start.sh ${HAPROXY_DOCKER_IMAGE}  ${HAPROXY_CONFIG}
sleep 3

echo ">>> ab"
ab -n 10000 -c ${CONCURRENCY} 127.0.0.1:8085/

echo ">>> haproxy_stop"
bash simple_bench/haproxy_stop.sh

echo ">>> simple_stop"
bash simple_bench/simple_stop.sh ${NUM_SERVERS}