export LD_LIBRARY_PATH := /usr/local/lib:$LD_LIBRARY_PATH
DIR := $(shell pwd)

compile:
	cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
	cmake --build build -j

clean:
	rm build/*

run:
	./build/opt ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

crun: compile
	./build/opt ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

cbuild: compile
	./build/opt --build-constraints $(PROTO_PATH) ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

csolve: compile
	./build/opt --solve $(PROTO_PATH) ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv $(OUTPUT_DIR)

cworkflow: compile
	@MODEL_PATH_DEFAULT=/tmp/awsome_model.pb; \
	MODEL_PATH=$${MODEL_PATH:-$$MODEL_PATH_DEFAULT}; \
	OUTPUT_DIR_DEFAULT=./results; \
	OUTPUT_DIR=$${OUTPUT_DIR:-$$OUTPUT_DIR_DEFAULT}; \
	echo "Building constraints to $$MODEL_PATH..."; \
	./build/opt --build-constraints $$MODEL_PATH ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv; \
	echo "Solving model from $$MODEL_PATH..."; \
	mkdir -p $$OUTPUT_DIR; \
	./build/opt --solve $$MODEL_PATH ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv $$OUTPUT_DIR

debug:
	gdb --args ./build/opt ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

ptest:
	python -m unittest ./tests/test_py.py
	python -m unittest ./tests/test_py_sp_only.py

ctest:
	python -m unittest ./tests/test_cpp_sp_only.py

dopt:
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs awsome-savings:optimizer /bin/sh -c "/optimizer/build/opt /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-logs/output > /optimizer-logs/output.log 2> /optimizer-logs/error.log"

# Docker build constraints only
# Usage: make dbuild PROTO_NAME=model.pb
dbuild:
	@mkdir -p $(DIR)/logs
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs awsome-savings:optimizer /bin/sh -c "/optimizer/build/opt --build-constraints /optimizer-logs/$(PROTO_NAME) /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv > /optimizer-logs/build.log 2> /optimizer-logs/build_error.log"

# Docker solve pre-built model
# Usage: make dsolve PROTO_NAME=model.pb
dsolve:
	@mkdir -p $(DIR)/logs/output
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs awsome-savings:optimizer /bin/sh -c "/optimizer/build/opt --solve /optimizer-logs/$(PROTO_NAME) /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-logs/output > /optimizer-logs/solve.log 2> /optimizer-logs/solve_error.log"

# Docker complete build+solve workflow
# Usage: make dworkflow [PROTO_NAME=awsome_model.pb]
dworkflow:
	@PROTO_NAME_DEFAULT=awsome_model.pb; \
	PROTO_NAME=$${PROTO_NAME:-$$PROTO_NAME_DEFAULT}; \
	mkdir -p $(DIR)/logs/output; \
	echo "Building constraints with Docker..."; \
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs awsome-savings:optimizer /bin/sh -c "/optimizer/build/opt --build-constraints /optimizer-logs/$$PROTO_NAME /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv > /optimizer-logs/build.log 2> /optimizer-logs/build_error.log"; \
	echo "Solving model with Docker..."; \
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs awsome-savings:optimizer /bin/sh -c "/optimizer/build/opt --solve /optimizer-logs/$$PROTO_NAME /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-logs/output > /optimizer-logs/solve.log 2> /optimizer-logs/solve_error.log"

# Docker build constraints only (equivalent to cbuild but using Docker)
# Usage: make dcbuild PROTO_PATH=/path/to/model.pb
dcbuild:
	@PROTO_DIR=$$(dirname $(PROTO_PATH)); \
	PROTO_FILE=$$(basename $(PROTO_PATH)); \
	echo "Building constraints with Docker and saving to: $(PROTO_PATH)"; \
	docker run -v $(DIR)/data:/optimizer-files -v $$PROTO_DIR:/optimizer-proto awsome-savings:optimizer /bin/sh -c "/optimizer/build/opt --build-constraints /optimizer-proto/$$PROTO_FILE /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv"

# Docker solve pre-built model (equivalent to csolve but using Docker)
# Usage: make dcsolve PROTO_PATH=/path/to/model.pb [OUTPUT_DIR=./results]
dcsolve:
	@PROTO_DIR=$$(dirname $(PROTO_PATH)); \
	PROTO_FILE=$$(basename $(PROTO_PATH)); \
	OUTPUT_DIR_DEFAULT=./results; \
	OUTPUT_DIR=$${OUTPUT_DIR:-$$OUTPUT_DIR_DEFAULT}; \
	mkdir -p $$OUTPUT_DIR; \
	echo "Solving model from $(PROTO_PATH) with Docker..."; \
	docker run -v $(DIR)/data:/optimizer-files -v $$PROTO_DIR:/optimizer-proto -v $$OUTPUT_DIR:/optimizer-output awsome-savings:optimizer /bin/sh -c "/optimizer/build/opt --solve /optimizer-proto/$$PROTO_FILE /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-output"

drun:
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs -it awsome-savings:optimizer /bin/sh

venv:
	python -m venv .venv
	./.venv/bin/python -m pip install -r requirements.txt

# Docker-based testing targets
docker-test-python:
	docker compose -f docker-compose.test.yml up --build python-tests

docker-test-cpp:
	docker compose -f docker-compose.test.yml up --build cpp-tests

docker-test-all:
	docker compose -f docker-compose.test.yml up --build all-tests

docker-test-clean:
	docker compose -f docker-compose.test.yml down --rmi all --volumes --remove-orphans

# Build test images
docker-build-test:
	docker build -f Dockerfile.python-test -t awsome-savings:python-test .
	docker build -f Dockerfile.cpp-test -t awsome-savings:cpp-test .

# Local testing with current environment
test-all: ptest ctest

# CI testing (uses Docker)
ci-test: docker-test-all
