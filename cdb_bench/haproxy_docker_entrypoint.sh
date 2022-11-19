#!/bin/sh
# https://github.com/docker-library/haproxy/blob/b07fcf19b4ee54ef37ffbf7241372961ddc97b8c/2.4/alpine/docker-entrypoint.sh
set -e

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]; then
  set -- haproxy "$@"
fi

if [ "$1" = 'haproxy' ]; then
  shift # "haproxy"
  # if the user wants "haproxy", let's add a couple useful flags
  #   -W  -- "master-worker mode" (similar to the old "haproxy-systemd-wrapper"; allows for reload via "SIGUSR2")
  #   -db -- disables background mode
  set -- haproxy -W -db "$@"
fi

exec "$@"