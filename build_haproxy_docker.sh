#!/bin/bash

echo ">>> Building HAProxy image (haproxy-2.4-alpine-dev)"
docker build -f haproxy-2.4-alpine-dev.Dockerfile -t haproxy-2.4-alpine-dev .
