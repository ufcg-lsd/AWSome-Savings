# AWSome Savings

AWSome Savings is a tool for optimizing costs in AWS EC2. AWS provides various market types for its instances, which have different pricing policies. The objetive is to determine how many instances should be allocated to each market, in order to satisfy the demand for those instances and minimize the cost. This tool is the implementation of a linear programming model (detailed description [here](https://www.overleaf.com/read/fyfghmzfkmtq)). It considers 3 markets: on-demand, reserve and savings plan.

## Dependencies

### Python
- Python 3.9
- [pandas](https://pandas.pydata.org/)  
- [OR-Tools](https://developers.google.com/optimization)  

### C++
- GCC / Clang with C++17 support  
- [CMake](https://cmake.org/)  
- [OR-Tools](https://github.com/google/or-tools) (v9.8)
- `build-essential`
- (Optional) Docker, if you prefer using the prebuilt container  

## Versions

There are three diferent versions of the optimization tool:
- py: implementation in Python, with the markets on-demand, reserves and savings plans;
- py_no_sp: implementation in Python, with the markets on-demand and savings plans;
- cpp_no_sp: implementation in C++, with the markets on-demand and savings plans.

## Directory structure

This repository contains the following directories:
- implementations: contains the implementation files for the different versions;
- data: contains sample data, as an example of the optimizer input;
- tests: contains tests for all the versions;
- util: contains auxiliary files, such as scripts for colleting memory and cpu usage.

## Python

There are two Python implementations, one that for the on-demand, reserves and savings plans markets and another for the on-demand and savings plans markets. The second one is faster if there is no need for using the reserve market. For running the optimizer model written in python, proceed with the following steps. 

### Installing dependencies

The tool is implemented in Python 3 and requires [pandas](https://pandas.pydata.org/) and [OR-Tools](https://developers.google.com/optimization). They can be installed using [pip](https://pypi.org/project/pip/):

```
pip install pandas
```

```
python3 -m pip install --upgrade --user ortools
```

### Using

There are several files with the input data for the simulation. For more information about them, see the documentation of ***build_simulation.py***. There are also examples of those files in the data folder.

#### Version with on-demand, reserves and savings plans

Run the follow command to perform an optimization:
```
python3 build_simulation.py {path of on_demand_config} {path of reserves_config} {path of savings_plan_config} {path of demand}
```
To run with the example files:
```
python3 implementations/py/build_simulation.py data/on_demand_config.csv data/reserves_config.csv data/savings_plan_config.csv data/total_demand.csv
```

#### Version with on-demand and savings plans

Run the follow command to perform an optimization:
```
python3 build_simulation.py {path of on_demand_config} {path of savings_plan_config} {path of demand}
```
To run with the example files:
```
python3 implementations/py_sp_only/build_simulation.py data/on_demand_config.csv data/savings_plan_config.csv data/total_demand.csv
```

#### Output

The simulation generates the following files as the output:
- result_cost: the total cost of the simulation, the cost for every instance and the total 
    savings plan cost;
- total_purchases_savings_plan: for every hour, the active value and the value reserved 
    for savings plan;
- total_purchases_{instance_name}: one file for every instance. It has, for every hour 
    and every market type (including savings plan), the number of active instances and 
    the number of reserves made.

### Tests

#### Version with on-demand, reserves and savings plans

The unit tests are in *tests/test_py.py* and are written using *unittest*. Currently, there are 12 tests of the model and 6 tests of the input validations. 

To run all tests, run the following command:
```
python3 -m unittest tests.test_py
```
To run a single test:
```
python3 -m unittest tests.test_py.TestAWSModel.{name of the test case}
```

#### Version with on-demand and savings plans

The unit tests are in *tests/test_py_sp_only.py* and are written using *unittest*. Currently, there are 6 tests of the model and 6 tests of the input validations. 

To run all tests, run the following command:
```
python3 -m unittest tests.test_py_sp_only
```
To run a single test:
```
python3 -m unittest tests.test_py_sp_only.TestAWSModel.{name of the test case}
```
### Debugging

The code generates logging when it runs. It is usefull for understanding, when one simulation cannot be completed (e.g. the amount of data was too much), where the code stopped working and how long took do run each step.

## C++

For running the optimizer model written in C++ proceed with the following steps. Currently, the version implemented in C++ has the on-demand and savings plans markets. 

### Installing dependencies

There are currently two possible ways to install the dependencies for the use of the model. It is possible to run and install everything locally and in a docker container with all dependencies an libraries installed.

#### Installing locally

For a local install, all the main tools for C++ developing are needed. Additionally, `cmake` and the `or-tools` library are needed for the local build. The following steps should result in a local binary of the optimizer ready to run:

1. Run the following command to install dependencies on Ubuntu:

```sh
sudo apt install -y build-essential cmake lsb-release
```

2. Clone the `or-tools` code for a local build and checkout to the compatible version with the optimizer:

```sh
git clone https://github.com/google/or-tools
git fetch --all --tags --prune
git checkout tags/v9.8 -b v9.8
```

3. Configure the build. This command configures the dependencies for local build.

```sh
cmake -S . -B build -DBUILD_DEPS=ON -DUSE_SCIP=OFF
```
> For faster executing, the `-DUSE_SCIP=OFF` flag is used. If you want to test the SCIP solver, remove the flag.

4. Build the source code.

> **Important**: The `-j` flag controls the number of parallel compilation jobs. For example, `-j4` runs up to 4 jobs in parallel. Higher values speed up the build but increase CPU usage. Using `-j` without a number will use all available cores/threads, which can heavily load or throttle your machine.

```sh
cmake --build build --config Release --target all -j4 -v
```

5. Install or-tools on your OS:
```sh
sudo cmake --build build --config Release --target install -v
```

This command will install the library to your [`CMAKE_INSTALL_PREFIX`](https://cmake.org/cmake/help/latest/variable/CMAKE_INSTALL_PREFIX.html) path (usually `/usr/local` on UNIX). You need to set your `LD_LIBRARY_PATH` variable to `lib/` inside the same path or the code won't compile:

```sh
export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
```

#### Getting the docker image

Another other option is to use the container that wraps all of C++ environment and OR-Tools library, having to only download the image and start the container.

- For downloading the image, use `docker pull` to retrieve it

    ```
    docker pull lsd/awsome-savings:latest
    ```

- For building the image, use `docker build` inside the cloned repository to build it locally

    ```
    docker build --network=host -t awsome-savings:latest .
    ```

### Compiling

If using the code locally, compiling it is necessary. Assuming the environment is setup correctly, compile the code with:

```
make compile
```

The binary will be located at `build/opt.elf`.

### Using

#### Binary

With a compiled binary, it's possible to run the optimization with:

```
./build/opt.elf {path of on_demand_config} {path of savings_plan_config} {path of demand}
```

For example, with the example files:
```
./build/opt.elf data/on_demand_config.csv data/savings_plan_config.csv data/total_demand.csv
```

> As a fourth optional parameter, is possible to add the path to the directory for saving the results. The current directory is the default (don't add the `/` to the end of the directory name)

#### Container

With the pulled image, run it interactively and add the path to the files as the volume that will be in `/optimizer-files` and the log directory as `/optimizer-logs` inside the container:

```
docker run -v {local path to files}/data:/optimizer-files -v {local path to logs}/logs:/optimizer-logs -it optimizer:latest /bin/sh
```

Inside the container, it's possible to run the commands as running locally:

```
./build/opt.elf /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-files > /optimizer-logs/output.log 2> /optimizer-logs/error.log
```

You can detach the container and leave it running the optimization or even run with as a daemon without interacting:
```
docker run -v {local path to files}/data:/optimizer-files -v {local path to logs}/logs:/optimzer-logs -d optimizer:latest /bin/sh -c "/optimizer/build/opt.elf /optimizer-files/on_demand_config.csv /optimizer-files/savings_plan_config.csv /optimizer-files/total_demand.csv /optimizer-files/output > /optimizer-logs/output.log 2> /optimizer-logs/error.log"
```

#### Output

The simulation generates the following files as the output:
- result_cost: the total cost of the simulation, the cost for every instance and the total 
    savings plan cost;
- total_purchases_savings_plan: for every hour, the active value and the value reserved 
    for savings plan;
- total_purchases_{instance_name}: one file for every instance. It has, for every hour 
    and every market type (including savings plan), the number of active instances and 
    the number of reserves made.

### Tests

The unit tests are in *tests/test_cpp.py* and are written using *unittest*. Currently, there are 6 tests of the model and 6 tests of the input validations. 

To run all tests, run the following command:
```
python3 -m unittest tests.test_cpp_sp_only
```
To run a single test:
```
python3 -m unittest tests.test_cpp_sp_only.TestAWSModel.{name of the test case}
```
### Debugging

The code generates logging when it runs. It is usefull for understanding, when one simulation cannot be completed (e.g. the amount of data was too much), where the code stopped working and how long took do run each step.
