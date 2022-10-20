#!/bin/bash

int_handler() {
    echo "Interrupted."
    kill $PPID
    exit 1
}
trap 'int_handler' INT

if [ "$#" -ne 1 ]
then
  echo "Require 1 argument(s) (NUM_NODES), $# provided"
  exit 1
fi

NUM_NODES=$1
if [ ${NUM_NODES} -lt 1 ]
then
  echo "Require at least 1 nodes"
  exit 1
fi
all_roaches="roach1"
for ((j = 2; j <= ${NUM_NODES}; j++)) do
  all_roaches+=",roach${j}"
done
echo "Spinning up roaches: ${all_roaches}"

echo "Terraforming a bridge network"
docker network create -d bridge roachnet

echo "Creating volumes"
for ((j = 1; j <= ${NUM_NODES}; j++)) do
  docker volume create roach${j}
done

echo "Running roach containers"
docker run -d --name=roach1 --hostname=roach1 --net=roachnet -p 26260:26257 -p 26261:8080  -v "roach1:/cockroach/cockroach-data" --platform linux/amd64  cockroachdb/cockroach:v22.1.9 start --insecure --join=${all_roaches}
for ((j = 2; j <= ${NUM_NODES}; j++)) do
  docker run -d --name=roach${j} --hostname=roach${j} --net=roachnet -v "roach${j}:/cockroach/cockroach-data" --platform linux/amd64 cockroachdb/cockroach:v22.1.9 start --insecure --join=${all_roaches}
done

echo "Initializing roach cluster"
docker exec -it roach1 ./cockroach init --insecure
docker exec -it roach1 grep 'node starting' cockroach-data/logs/cockroach.log -A 11

echo "Swarm of ${NUM_NODES} roaches started (psql at 26260, console at 26261)"
