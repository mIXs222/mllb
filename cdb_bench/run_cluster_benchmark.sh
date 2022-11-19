#!/bin/bash

docker exec -it roach1 ./cockroach workload init tpcc 'postgresql://root@haproxy:26257?sslmode=disable'
docker exec -it roach1 ./cockroach workload run tpcc --duration=5m 'postgresql://root@haproxy:26257?sslmode=disable'