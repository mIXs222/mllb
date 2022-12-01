#!/bin/bash

# Clear state by:
#   bash simple_bench/haproxy_stop.sh; simple_bench/simple_stop.sh 4

int_handler() {
    echo "Interrupted."
    kill $PPID
    exit 1
}
trap 'int_handler' INT

CONFIGS=(
  "simple_bench/haproxy_lc_simple4.cfg"
  "simple_bench/haproxy_rand2_simple4.cfg"
  "simple_bench/haproxy_rand_simple4.cfg"
  "simple_bench/haproxy_rr_simple4.cfg"
  "simple_bench/haproxy_ml_simple4.cfg"
)

bash build_haproxy_docker.sh
for ((i = 0; i < ${#CONFIGS[@]}; i++)) do
  echo "=============================================================="
  echo "=== ${CONFIGS[$i]}"
  echo "=============================================================="
  bash simple_bench/bench.sh haproxy-2.4-alpine-dev ${CONFIGS[$i]} 4
done