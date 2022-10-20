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
  all_roaches+=" roach${j}"
done
echo "Terminating roaches: ${all_roaches}"
docker stop ${all_roaches}
docker rm ${all_roaches}
docker volume rm ${all_roaches}
docker network rm roachnet
