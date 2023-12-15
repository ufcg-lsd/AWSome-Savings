## AWSome Savings

AWSome Savings is a tool for optimizing costs in AWS EC2. AWS provides various market types for its instances, which have different pricing policies. The objetive is to determine how many instances should be allocated to each market, in order to satisfy the demand for those instances and minimize the cost. This tool is the implementation of a linear programming model (detailed description [here](https://www.overleaf.com/read/fyfghmzfkmtq)). It considers 3 markets: on-demand, reserve and savings plan.

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
python -m unittest
```
To run a single test:
```
python -m unittest tests.test_aws_model.TestAWSModel.{name of the test case}
```
### Debugging

The code generates logging when it runs. It is usefull for understanding, when one simulation cannot be completed (e.g. the amount of data was too much), where the code stopped working and how long took do run each step.
