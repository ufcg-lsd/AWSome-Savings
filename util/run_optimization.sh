#!/bin/sh

output_directory="$1"

./collect-cpu-usage.sh > "$output_directory/cpu_output.csv" &
./collect-memory-usage.sh > "$output_directory/memory_output.csv" &

nohup ./build/opt.elf /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-files/output >/optimizer-logs/output.log 2>/optimizer-logs/error.log

ps -ef | grep collect-cpu-usage.sh | grep -v grep | awk '{ print $1 }' | xargs kill -9
ps -ef | grep collect-memory-usage.sh | grep -v grep | awk '{ print $1 }' | xargs kill -9
