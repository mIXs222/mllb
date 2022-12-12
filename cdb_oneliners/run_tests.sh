#!/bin/bash

#TO USE: First, run "docker-compose up -d" and verify the ycsb-init client is loading values succesfully using docker ps
#then run script, with defined number of loops to run. Each loop corresponds with 10000 operations from 10 unique clients
if [ "$#" -ne 2 ]
then
  echo "Require 2 argument(s) (NUM_ITERATIONS) (OUTPUT_DIR), $# provided"
  echo "Note: each iteration corresponds with 10000 sql operations"
  exit 1
fi

NUM_ITERS=$1
OUT_DIR=$2
if [ ${NUM_ITERS} -lt 1 ]
then
  echo "Require at least 1 iteration"
  exit 1
fi

#Start containers..wait
docker-compose up -d
sleep 5s

for ((i = 0; i < ${NUM_ITERS}; i++)) do
   bash gather_and_reset.sh
done

#Now get the log outputs (since we restart containers each has all iterations stored)
echo "gathering log outputs from clients"
docker-compose ps | grep ycsb-client | awk '{print $1}' | while read -r line;
do
   docker-compose logs $line >> ${OUT_DIR}/$line.txt;
done

docker-compose down
