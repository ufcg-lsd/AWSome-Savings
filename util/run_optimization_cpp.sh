#!/bin/sh

output_directory="$1"
logs_directory="$2"

./collect-cpu-usage.sh > "$logs_directory/cpu_output.csv" &
./collect-memory-usage.sh > "$logs_directory/memory_output.csv" &

nohup ./build/opt.elf "$output_directory/on_demand_config.csv" "$output_directory/savings_plan_config.csv" "$output_directory/total_demand.csv" "$output_directory/output" > "$logs_directory/output.log" 2> "$logs_directory/error.log"

ps -ef | grep collect-cpu-usage.sh | grep -v grep | awk '{ print $1 }' | xargs kill -9
ps -ef | grep collect-memory-usage.sh | grep -v grep | awk '{ print $1 }' | xargs kill -9
