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

debug:
	gdb --args ./build/opt ./data/on_demand_config.csv ./data/savings_plan_config.csv ./data/total_demand.csv

ptest:
	python -m unittest ./tests/test_py.py
	python -m unittest ./tests/test_py_sp_only.py

ctest:
	python -m unittest ./tests/test_cpp_sp_only.py

dopt:
	docker run -v $(DIR)/data:/optimizer-files -v $(DIR)/logs:/optimizer-logs awsome-savings:optimizer /bin/sh -c "/optimizer/build/opt /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-logs/output > /optimizer-logs/output.log 2> /optimizer-logs/error.log"

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
