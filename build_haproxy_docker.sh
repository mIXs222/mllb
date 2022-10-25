#!/bin/bash

echo ">>> Building HAProxy image (haprox-2.4-alpine-dev)"
docker build -f haprox-2.4-alpine-dev.Dockerfile -t haprox-2.4-alpine-dev .
