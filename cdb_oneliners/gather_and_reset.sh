#!/bin/bash

#echo "==================================="
#echo "Gathering logs from clients into logs.txt"
#echo "==================================="
#docker-compose ps | grep ycsb-client | awk '{print $1}' | while read -r line;
#do
#   docker-compose logs $line >> output.txt;
#done

echo "==================================="
echo "Restarting clients"
echo "==================================="
docker-compose ps | grep ycsb-client | awk '{print $1}' | while read -r line;
do
    docker-compose restart $line
done