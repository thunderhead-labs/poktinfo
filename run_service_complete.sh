#!/bin/bash

SERVICE=$1

# ./run_service_history.sh service_name
if [ $SERVICE == "rewards" ]; then
  export service_path="/home/debian/chain_service/run_rewards.py"
elif [ $SERVICE == "nodes" ]; then
  export service_path="/home/debian/chain_service/run_nodes.py"
elif [ $SERVICE == "errors" ]; then
  export service_path="/home/debian/errors_service/run_errors_cache.py"
elif [ $SERVICE == "latency" ]; then
  export service_path="/home/debian/errors_service/run_latency_cache.py"
else
  export service_path=""
fi
nohup python3 $service_path complete &
