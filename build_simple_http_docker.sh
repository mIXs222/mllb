#!/bin/bash

echo ">>> Building simple HTTP server (simple-http-server-dev)"
cd simple-docker-http-server
docker build -f Dockerfile -t simple-http-server-dev .
cd ..
