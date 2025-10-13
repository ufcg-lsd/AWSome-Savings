#!/bin/sh

set -eu

output_directory="$1"
logs_directory="$2"
proto_path="$3"

# Function to cleanup collectors
cleanup_collectors() {
    ps -ef | grep collect-cpu-usage.sh | grep -v grep | awk '{ print $2 }' | xargs kill -9 2>/dev/null || true
    ps -ef | grep collect-memory-usage.sh | grep -v grep | awk '{ print $2 }' | xargs kill -9 2>/dev/null || true
}

# Start collectors
./collect-cpu-usage.sh > "$logs_directory/solve_cpu_output.csv" &
./collect-memory-usage.sh > "$logs_directory/solve_memory_output.csv" &

nohup /optimizer/build/opt --solve "$proto_path" "$output_directory/on_demand_config.csv" "$output_directory/savings_plan_config.csv" "$output_directory/total_demand.csv" "$logs_directory" > "$logs_directory/solve_output.log" 2> "$logs_directory/solve_error.log"
opt_exit_code=$?
