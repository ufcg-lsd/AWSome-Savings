bash collect-cpu-usage.sh > cpu_output.csv 2>/dev/null &
bash collect-memory-usage.sh > memory_output.csv 2>/dev/null &
nohup make run >logs.txt 2>logs.txt
ps -ef | grep collect-cpu-usage.sh | awk '{ print $2 }' | xargs kill -9
ps -ef | grep collect-memory-usage.sh | awk '{ print $2 }' | xargs kill -9
