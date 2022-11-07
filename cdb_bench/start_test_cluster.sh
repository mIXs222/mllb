#!/bin/bash

int_handler() {
    echo "Interrupted."
    kill $PPID
    exit 1
}
trap 'int_handler' INT

if [ "$#" -ne 2 ]
then
  echo "Require 3 argument(s) (NUM_NODES) (SLOW_NODES)... $# provided"
  exit 1
fi

NUM_NODES=$1
SLOW_NODES=$2

if [ ${NUM_NODES} -lt 1 ]
then
  echo "Require at least 1 nodes"
  exit 1
fi

if [ ${SLOW_NODES} -gt ${NUM_NODES} ]
then
  echo "Require less slow nodes than number of nodes..."
  exit 1
fi

echo "Creating volumes"
all_roaches=""
for ((j = 1; j <= ${NUM_NODES}; j++)) do
  all_roaches+="roach${j},"
  docker volume create roach${j}
done

all_roaches=${all_roaches%?} #delete last comma from string

echo "Spinning up roaches: ${all_roaches}"

echo "Terraforming a bridge network"
docker network create -d bridge roachnet

for ((j = 1; j <= ${NUM_NODES}; j++)) do
  docker volume create roach${j}
done

echo "Running slow roach containers"
for ((i = 1; i <= ${SLOW_NODES}; i++)) do
  docker run -d --name=roach${i} --hostname=roach${i} --net=roachnet  --cpus 2 -v "roach${i}:/cockroach/cockroach-data" --platform linux/amd64 cockroachdb/cockroach:v22.1.9 start --insecure --join=${all_roaches}
done

echo "Running normal roach containers"
for ((j = $((SLOW_NODES + 1)); j <= ${NUM_NODES}; j++)) do
  docker run -d --name=roach${j} --hostname=roach${j} --net=roachnet --cpus 4 -v "roach${j}:/cockroach/cockroach-data" --platform linux/amd64 cockroachdb/cockroach:v22.1.9 start --insecure --join=${all_roaches}
done

echo "Initializing roach cluster"
docker exec -it roach1 ./cockroach init --insecure
docker exec -it roach1 grep 'node starting' cockroach-data/logs/cockroach.log -A 11

echo "Swarm of ${NUM_NODES} roaches started (psql at 26260, console at 26261)"

#Starting HAProxy Container
echo "Generating HAProxy configuration at haproxy.cfg"
docker exec -it roach1 ./cockroach gen haproxy --certs-dir=certs --host=roach1 --port=26257 --insecure
docker cp roach1:/cockroach/haproxy.cfg haproxy.cfg

docker run -d --name haproxy --net roachnet  --cpus $((NUM_NODES+1)) -v $(pwd):/usr/local/etc/haproxy:ro -p 26257:26257 -p 8404:8404 haproxytech/haproxy-alpine:2.4

echo "HAProxy LB started, bounded to $((NUM_NODES+1)) cores"