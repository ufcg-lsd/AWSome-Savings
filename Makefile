export LD_LIBRARY_PATH := /usr/local/lib:$LD_LIBRARY_PATH
DIR := $(shell pwd)

compile:
	g++ -g -O3 -c cpp/aws_model.cpp -o cpp/build/aws_model.o
	g++ -g -O3 -c cpp/build_simulation.cpp -o cpp/build/build_simulation.o
	g++ -g -O3 -c cpp/csv_parser.cpp -o cpp/build/csv_parser.o
	g++ -g -O3 -c cpp/validations.cpp -o cpp/build/validations.o
	g++ -g -O3 cpp/build/aws_model.o cpp/build/build_simulation.o cpp/build/csv_parser.o cpp/build/validations.o -o cpp/build/opt.elf -lortools -labsl_log_internal_message

docker-compile:
	g++ -g -O3 -c aws_model.cpp -o build/aws_model.o
	g++ -g -O3 -c build_simulation.cpp -o build/build_simulation.o
	g++ -g -O3 -c csv_parser.cpp -o build/csv_parser.o
	g++ -g -O3 -c validations.cpp -o build/validations.o
	g++ -g -O3 build/aws_model.o build/build_simulation.o build/csv_parser.o build/validations.o -o build/opt.elf -lortools -labsl_log_internal_message

clean:
	rm build/*

run:
	./build/opt.elf ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

crun: compile
	./build/opt.elf ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

debug:
	gdb --args ./build/opt.elf ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

ptest:
	python -m unittest ./tests/test_aws_model.py

ctest:
	python -m unittest ./tests/test_aws_model_cpp.py

dopt:
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimzer-logs optimizer:latest /bin/sh -c "/optimizer/build/opt.elf /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-files/output > /optimizer-logs/output.log 2> /optimizer-logs/error.log"

drun:
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs -it optimizer:latest /bin/sh
