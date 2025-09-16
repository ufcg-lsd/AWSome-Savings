export LD_LIBRARY_PATH := /usr/local/lib:$LD_LIBRARY_PATH
DIR := $(shell pwd)

compile:
	mkdir -p build
	g++ -g -O3 -c implementations/cpp_sp_only/aws_model.cpp -o implementations/cpp_sp_only/build/aws_model.o
	g++ -g -O3 -c implementations/cpp_sp_only/build_simulation.cpp -o implementations/cpp_sp_only/build/build_simulation.o
	g++ -g -O3 -c implementations/cpp_sp_only/csv_parser.cpp -o implementations/cpp_sp_only/build/csv_parser.o
	g++ -g -O3 -c implementations/cpp_sp_only/validations.cpp -o implementations/cpp_sp_only/build/validations.o
	g++ -g -O3 implementations/cpp_sp_only/build/aws_model.o implementations/cpp_sp_only/build/build_simulation.o implementations/cpp_sp_only/build/csv_parser.o implementations/cpp_sp_only/build/validations.o -o build/opt.elf -lortools -labsl_log_internal_message

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
	python -m unittest ./tests/test_py.py
	python -m unittest ./tests/test_py_sp_only.py

ctest:
	python -m unittest ./tests/test_cpp_sp_only.py

dopt:
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimzer-logs optimizer:latest /bin/sh -c "/optimizer/build/opt.elf /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-files/output > /optimizer-logs/output.log 2> /optimizer-logs/error.log"

drun:
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs -it optimizer:latest /bin/sh

venv:
	python -m venv .venv
	./.venv/bin/python -m pip install -r requirements.txt
