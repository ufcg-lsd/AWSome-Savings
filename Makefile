export LD_LIBRARY_PATH := /usr/local/lib:$LD_LIBRARY_PATH

compile:
	g++ -g -c aws_model.cpp -o build/aws_model.o
	g++ -g -c build_simulation.cpp -o build/build_simulation.o
	g++ -g -c csv_parser.cpp -o build/csv_parser.o
	g++ -g -c validations.cpp -o build/validations.o
	g++ -g build/aws_model.o build/build_simulation.o build/csv_parser.o build/validations.o -o build/opt.elf -lortools -labsl_log_internal_message

clean:
	rm build/*

run:
	./build/opt.elf ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

crun: compile
	./build/opt.elf ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

debug:
	gdb ./build/opt.elf ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

ptest:
	python -m unittest ./tests/test_aws_model.py

ctest:
	python -m unittest ./tests/test_aws_model_cpp.py
