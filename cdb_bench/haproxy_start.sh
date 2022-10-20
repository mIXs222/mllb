#!/bin/bash

echo "Generating HAProxy configuration at haproxy.cfg"
docker exec -it roach1 ./cockroach gen haproxy --certs-dir=certs --host=roach1 --port=26257 --insecure
docker cp roach1:/cockroach/haproxy.cfg haproxy.cfg

docker run -d --name haproxy --net roachnet -v $(pwd):/usr/local/etc/haproxy:ro -p 26257:26257 -p 8404:8404 haproxytech/haproxy-alpine:2.4
