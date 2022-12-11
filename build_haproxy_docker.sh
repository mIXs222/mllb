#!/bin/bash

echo ">>> Building HAProxy image (haproxy-2.4-alpine-dev)"
DOCKER_BUILDKIT=1 docker build -f haproxy-2.4-alpine-dev.Dockerfile -t alecdray22/dynamic-haproxy:latest .
#docker push alecdray22/dynamic-haproxy:latest
