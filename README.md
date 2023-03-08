## AWSome Savings


Run the follow command to perform an optmization:
```
python3 build-simulation.py
```

### Tests

The unit tests are in tests/aws_model_tests.py and are written using *unittest*. Currently, there are 12 tests of the model and 6 tests of the input validations. To run the tests, go to the folder tests and run the command:
```
python -m unittest aws_model_tests.py
```
To run a single test:
```
python -m unittest aws_model_tests.TestAWSModel.{name of the test case}
```
