#!/bin/bash
SERVICE=$1
echo $SERVICE
# ./run_service_history.sh service_name start_block end_block
if [ $SERVICE == "rewards" ]; then
  service_path="/home/debian/chain_service/run_rewards.py"
elif [ $SERVICE == "nodes" ]; then
  service_path="/home/debian/chain_service/run_nodes.py"
elif [ $SERVICE == "errors" ]; then
  service_path="/home/debian/errors_service/run_errors_cache.py"
elif [ $SERVICE == "latency" ]; then
  export service_path="/home/debian/errors_service/run_latency_cache.py"
else
  service_path=""
fi
echo $service_path
nohup python3 $service_path history $2 $3 &
