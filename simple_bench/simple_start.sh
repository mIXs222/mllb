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

echo "Running roach containers"
docker run -d --name=roach1 --hostname=roach1 --net=roachnet simple-http-server-dev
for ((j = 2; j <= ${NUM_NODES}; j++)) do
  docker run -d --name=roach${j} --hostname=roach${j} --net=roachnet simple-http-server-dev
done

echo "Swarm of ${NUM_NODES} roaches started"
