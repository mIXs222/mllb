#!/bin/bash

echo "Stopping HAProxy"
docker stop haproxy
docker rm haproxy