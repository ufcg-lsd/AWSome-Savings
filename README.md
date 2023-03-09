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

There are several files with the input data for the simulation. For more information about them, see the documentation of ***build-simulation.py***. There are also examples of those files in the data folder.

Run the follow command to perform an optimization:
```
python3 build-simulation.py
```


