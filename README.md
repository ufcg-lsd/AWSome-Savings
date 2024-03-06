# AWSome Savings

AWSome Savings is a tool for optimizing costs in AWS EC2. AWS provides various market types for its instances, which have different pricing policies. The objetive is to determine how many instances should be allocated to each market, in order to satisfy the demand for those instances and minimize the cost. This tool is the implementation of a linear programming model (detailed description [here](https://www.overleaf.com/read/fyfghmzfkmtq)). It considers 3 markets: on-demand, reserve and savings plan.

## Python

For running the optimizer model written in python, proceed with the following steps.

### Installing dependencies

The tool is implemented in Python 3 and requires [pandas](https://pandas.pydata.org/) and [OR-Tools](https://developers.google.com/optimization). They can be installed using [pip](https://pypi.org/project/pip/):

```
pip install pandas
```

```
python -m pip install --upgrade --user ortools
```

### Using

There are several files with the input data for the simulation. For more information about them, see the documentation of ***build_simulation.py***. There are also examples of those files in the data folder.

Run the follow command to perform an optimization:
```
python3 build_simulation.py {path of on_demand_config} {path of savings_plan_config} {path of demand}
```
To run with the example files:
```
python3 build_simulation.py data/on_demand_config.csv data/savings_plan_config.csv data/total_demand.csv
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

The unit tests are in *tests/test_aws_model.py* and are written using *unittest*. Currently, there are 12 tests of the model and 6 tests of the input validations. 

To run all tests, run the following command:
```
python -m unittest tests.test_aws_model
```
To run a single test:
```
python -m unittest tests.test_aws_model.TestAWSModel.{name of the test case}
```
### Debugging

The code generates logging when it runs. It is usefull for understanding, when one simulation cannot be completed (e.g. the amount of data was too much), where the code stopped working and how long took do run each step.

## C++

For running the optimizer model written in C++, proceed with the following steps.

### Installing dependencies

There are currently two possible ways to install the dependencies for the use of the model. It is possible to run and install everything locally and in a docker container with all dependencies an libraries installed.

#### Installing locally

For a local install, all the main tools for C++ developing are needed (`gcc`, `g++`), normally included in packages such as `build-essential` in apt. Additionally, `cmake` and the `or-tools` library are needed for the local build.

After installing the C++ developing tools and `cmake`, seek to the [OR-Tools building manual](https://developers.google.com/optimization/install/cpp) for building the library locally or installing the binaries.

> Important: the code will not run if `LD_LIBRARY_PATH` variable is not set correctly pointing to the path of the installation of OR-Tools.

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

If using the code locally, compiling it is necessary. Assuming all the environment is setup correctly, compile the code with:

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

If you want to run your calcs and optimizations inside the container, you may need to set the volumes:
```
docker run -v {input-file.csv}:/calculation/calculation-file.csv -v {output_dir}:/calculation/final-result -v {logs_dir}:/calculation/logs -it awsome-savings:latest bash
```

##### Optimization

Inside the container, it's possible to run the commands as running locally:
```
python3 costplanner_cli.py calculation-file.csv final-result --m optimal > logs/output.log 2> logs/error.log
```

You can detach the container and leave it running the optimization or even run with as a daemon without interacting:
```
docker run -v {input_dir}:/calculation/calculation-file.csv -v {output_dir}:/calculation/final-result -v {logs_dir}:/calculation/optimizer-logs -d awsome-savings:latest bash -c "python3 costplanner_cli.py calculation-file.csv final-result --m optimal > /calculation/optimizer-logs/output.log 2> /calculation/optimizer-logs/error.log"
```

##### Calculation

Inside the container, it's possible to run the commands as running locally:
```
python3 costplanner_cli.py calculation-file.csv final-result --m classic --p proportion {ond_proportion} {noup_proportion} {partialup_proportion} {allup_proportion} --summarize > logs/output.log 2> logs/error.log
```

You can detach the container and leave it running the optimization or even run with as a daemon without interacting:
```
docker run -v {input_dir.csv}:/calculation/calculation-file.csv -v {output_dir}:/calculation/final-result -v {logs_dir}:/calculation/calculation-logs -d awsome-savings:latest bash -c "python3 costplanner_cli.py calculation-file.csv final-result --m classic --p proportion {ond_proportion} {noup_proportion} {partialup_proportion} {allup_proportion} --summarize > /calculation/calculation-logs/output.log 2> /calculation/calculation-logs/error.log"
```

#### Output

The simulation generates a file with the total cost for calculation, and the allocation recomended to the optimization as the output on the output volume.

### Tests

The unit tests are in *tests/test_aws_model.py* and are written using *unittest*. Currently, there are 12 tests of the model and 6 tests of the input validations. 

To run all tests, run the following command:
```
python -m unittest tests.test_aws_model_cpp
```
To run a single test:
```
python -m unittest tests.test_aws_model_cpp.TestAWSModel.{name of the test case}
```
### Debugging

The code generates logging when it runs. It is usefull for understanding, when one simulation cannot be completed (e.g. the amount of data was too much), where the code stopped working and how long took do run each step.
