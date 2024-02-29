export LD_LIBRARY_PATH := /usr/local/lib:$LD_LIBRARY_PATH
DIR := $(shell pwd)

build:
	docker build --network=host -t awsome-savings:latest .

compile:
	g++ -g -O3 -c aws_model.cpp -o build/aws_model.o
	g++ -g -O3 -c build_simulation.cpp -o build/build_simulation.o
	g++ -g -O3 -c csv_parser.cpp -o build/csv_parser.o
	g++ -g -O3 -c validations.cpp -o build/validations.o
	g++ -g -O3 build/aws_model.o build/build_simulation.o build/csv_parser.o build/validations.o -o build/opt.elf -lortools -labsl_log_internal_message

clean:
	rm build/*

run-optimizer:
	docker run -v $(input_dir):/calculation/calculation-file.csv -v $(output_dir):/calculation/final-result -v $(logs_dir):/calculation/optimizer-logs -d awsome-savings:latest bash -c "python3 costplanner_cli.py calculation-file.csv final-result --m optimal > /calculation/optimizer-logs/output.log 2> /calculation/optimizer-logs/error.log"

run-classic:
	docker run -v $(input_dir):/calculation/calculation-file.csv -v $(output_dir):/calculation/final-result -v $(logs_dir):/calculation/optimizer-logs -d awsome-savings:latest bash -c "python3 costplanner_cli.py calculation-file.csv final-result --m classic --p proportion $(ond_proportion) $(noup_proportion) $(partialup_proportion) $(allup_proportion) --summarize > /calculation/optimizer-logs/output.log 2> /calculation/optimizer-logs/error.log"

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
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs -it awsome-savings:latest /bin/sh

pull-awsome-savings:
	docker pull registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings
	docker image tag registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings awsome-savings:latest