## AWSome Savings


Run the follow command to perform an optmization:
```
python3 build-simulation.py
```

### Tests

The unit tests are in *tests/test_aws_model.py* and are written using *unittest*. Currently, there are 12 tests of the model and 6 tests of the input validations. 

To run all tests, go to the folder tests and run the command:
```
python -m unittest
```
To run a single test:
```
python -m unittest tests/test_aws_model.TestAWSModel.{name of the test case}
```

### Debugging

The code generates logging when it runs. It is usefull for understanding, when one simulation cannot be completed (e.g. the amount of data was too much), where the code stopped working and how long took do run each step.
