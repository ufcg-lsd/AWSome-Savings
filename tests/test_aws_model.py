""" Tests for the model.
"""

import unittest
import pandas as pd
import os
import subprocess

class TestAWSModel(unittest.TestCase):

    def safe_remove(self, path):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    def tearDown(self):

        self.safe_remove('on_demand_config.csv')
        self.safe_remove('reserves_config.csv')
        self.safe_remove('savings_plan_config.csv')
        self.safe_remove('total_demand.csv')
        self.safe_remove('result_cost.csv')

    # def test_ex(self):
    #     on_demand_config = {'instance': [],
    #                         'hourly_price': []}

    #     on_demand_df = pd.DataFrame(on_demand_config)
    #     on_demand_df.to_csv('on_demand_config.csv', index=False)

    #     reserves_config = {'instance': [],
    #                         'market_name': [],
    #                         'hourly_price': [],
    #                         'upfront_price': [],
    #                         'duration': []}

    #     reserves_df = pd.DataFrame(reserves_config)
    #     reserves_df.to_csv('reserves_config.csv', index=False)

    #     savings_plan_config = {'instance': [],
    #                             'hourly_price': [],
    #                             'duration': []}

    #     savings_plan_df = pd.DataFrame(savings_plan_config)
    #     savings_plan_df.to_csv('savings_plan_config.csv', index=False)

    #     demand = {'Hour': []}

    #     demand_df = pd.DataFrame(demand)
    #     demand_df.to_csv('total_demand.csv', index=False)

    #     os.system(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv')

    #     try:
    #         #only checks the total cost
    #         result_cost = pd.read_csv('result_cost.csv')
    #         actual_cost = result_cost.loc[0, 'total_cost']
    #         self.assertEqual(actual_cost, 0)
    #     except FileNotFoundError:
    #         self.fail("The file result_cost.csv was not created.")

    #1
    def test_savings_plan(self):
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [1, 1],
                            'upfront_price': [0, 0],
                            'duration': [4, 4]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4],
                  'a': [10, 10, 5, 5],
                  'b': [5, 5, 10, 10]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run('python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 60)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #2
    def test_on_demand_reserved(self):
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [1, 1],
                            'upfront_price': [0, 0],
                            'duration': [5, 5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1.1, 1.1],
                                'duration': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 20, 20, 20, 20, 30],
                  'b': [10, 20, 20, 20, 20, 30]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 280)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #3
    def test_savings_plan_on_demand(self):
        #very similar to the previous test, test_on_demand_reserved
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [1.1, 1.1],
                            'upfront_price': [0, 0],
                            'duration': [5, 5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 20, 20, 20, 20, 30],
                  'b': [10, 20, 20, 20, 20, 30]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 280)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #4
    def test_savings_plan_reserved(self):
        #very similar to the previous tests, test_on_demand_reserved and test_savings_plan_on_demand
        #in this test, there is no difference in cost in allocating instances for savings plan or reserved
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [1, 1],
                            'upfront_price': [0, 0],
                            'duration': [5, 5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 20, 20, 20, 20, 30],
                  'b': [10, 20, 20, 20, 20, 30]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 280)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #5
    def test_savings_plan_in_the_future(self):
        #the savings plan reserve goes beyond the simulation period
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [20, 20]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [20, 20],
                            'upfront_price': [0, 0],
                            'duration': [4, 4]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4],
                  'a': [10, 10, 5, 5],
                  'b': [5, 5, 10, 10]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 75)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #6
    def test_savings_plan_reserve_different_durations(self):
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [4, 4]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [1.5, 1.5],
                            'upfront_price': [0, 0],
                            'duration': [2, 2]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 7, 6, 12, 5, 5], 
                  'b': [5, 8, 9, 3, 4, 4]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 87)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #7
    def test_savings_plan_reserve_different_durations_2(self):
        #similar to 6, but uses only savings plan
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [4, 4]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [2.1, 2.1],
                            'upfront_price': [0, 0],
                            'duration': [2, 2]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 7, 6, 12, 5, 5], 
                  'b': [5, 8, 9, 3, 4, 4]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 96)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #8
    def test_savings_plan_reserve_on_demand(self):
        #similar to 6
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [2.5, 2.5]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [1.5, 1.5],
                            'upfront_price': [0, 0],
                            'duration': [2, 2]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 7, 6, 12, 5, 6], 
                  'b': [5, 8, 9, 3, 4, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 97)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #9
    def test_savings_plan_different_prices(self):
        #In this test, we got the expected cost from running the tool. We checked that it respect the rules. 
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [4, 4]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'hourly_price': [20, 20],
                            'upfront_price': [0, 0],
                            'duration': [4, 4]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [3, 1],
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [3, 4, 6, 0, 0, 0], 
                  'b': [0, 0, 0, 15, 20, 23]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 120)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #10
    def test_randon(self):
        #In this test, we got the expected cost from running the tool. We checked that it respect the rules. 
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [3, 7, 1.5]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b', 'c'],
                            'market_name': ['reserved', 'reserved', 'reserved'],
                            'hourly_price': [0.8, 1.5, 0.4],
                            'upfront_price': [0, 0, 0],
                            'duration': [5, 5, 5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [1, 2, 0.5],
                                'duration': [5, 5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 11, 9, 32, 3, 0],
                  'b': [3, 7, 4, 2, 9, 10], 
                  'c': [38, 24, 42, 2, 17, 13]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(round(actual_cost), 244)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #11
    def test_one_instance_type(self):
        on_demand_config = {'instance': ['a'],
                            'hourly_price': [2.2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a'],
                            'market_name': ['reserved'],
                            'hourly_price': [1],
                            'upfront_price': [0],
                            'duration': [5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a'],
                                'hourly_price': [1.2],
                                'duration': [2]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 15, 15, 10, 10, 10]} 

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 84)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")
    
    #12
    def test_multiple_reserve_markets(self):
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [4, 8]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        #effective hourly rate: no_up = 1,2; partial_up = 1.5,3; no_up = 2,4
        reserves_config = {'instance': ['a', 'b', 'a', 'b', 'a', 'b'],
                            'market_name': ['all_up', 'all_up', 'partial_up', 'partial_up', 'no_up', 'no_up'],
                            'hourly_price': [0, 0, 0.75, 1.5, 2, 4],
                            'upfront_price': [4, 8, 3, 6, 0, 0],
                            'duration': [4, 4, 4, 4, 4, 4]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [4, 8], #we don't want to reserve savings plan
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4],
                  'a': [3, 3, 3, 3], 
                  'b': [2, 2, 2, 2]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(round(actual_cost), 28)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #tests checking validations

    #13
    def test_more_instances_total_demand(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b', 'c'],
                            'market_name': ['all_up', 'all_up', 'all_up'],
                            'hourly_price': [0, 0, 0],
                            'upfront_price': [2, 2.6, 4],
                            'duration': [3, 3, 3]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [0.7, 0.9, 1.3],
                                'duration': [3, 3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'a': [1, 2, 0],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)
        
        out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 29.9)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #14
    def test_invalid_savings_plan_durations(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b', 'c'],
                            'market_name': ['reserved', 'reserved', 'reserved'],
                            'hourly_price': [0, 0, 0],
                            'upfront_price': [2, 2.6, 4],
                            'duration': [3, 3, 3]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [0.7, 0.9, 1.3],
                                'duration': [2, 3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'a': [1, 2, 0],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        with self.assertRaises(Exception):
            out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, check=True)

    #15
    def test_different_reserve_markets(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b', 'c','c'],
                            'market_name': ['all_up', 'all_up', 'all_up', 'no_up'],
                            'hourly_price': [0, 0, 0, 1.5],
                            'upfront_price': [2, 2.6, 4, 0],
                            'duration': [3, 3, 3, 3]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [0.7, 0.9, 1.3],
                                'duration': [3, 3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'a': [1, 2, 0],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        with self.assertRaises(Exception):
            out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, check=True)

    #16
    def test_different_instances_reserves_config(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b', 'c', 'd'],
                            'market_name': ['all_up', 'all_up', 'all_up', 'all_up'],
                            'hourly_price': [0, 0, 0, 0],
                            'upfront_price': [2, 2.6, 4, 4],
                            'duration': [3, 3, 3, 3]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [0.7, 0.9, 1.3],
                                'duration': [3, 3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'a': [1, 2, 0],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        with self.assertRaises(Exception):
            out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, check=True)

    #17
    def test_different_instances_savings_plan_config(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b', 'c'],
                            'market_name': ['all_up', 'all_up', 'all_up'],
                            'hourly_price': [0, 0, 0],
                            'upfront_price': [2, 2.6, 4],
                            'duration': [3, 3, 3]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'c'],
                                'hourly_price': [0.7, 1.3],
                                'duration': [3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'a': [1, 2, 0],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        with self.assertRaises(Exception):
            out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, check=True)

    #18
    def test_different_instances_total_demand(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b', 'c'],
                            'market_name': ['all_up', 'all_up', 'all_up'],
                            'hourly_price': [0, 0, 0],
                            'upfront_price': [2, 2.6, 4],
                            'duration': [3, 3, 3]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [0.7, 0.9, 1.3],
                                'duration': [3, 3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('total_demand.csv', index=False)

        with self.assertRaises(Exception):
            out = subprocess.run(' python3 build_simulation.py on_demand_config.csv reserves_config.csv savings_plan_config.csv total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, check=True)  

    #TO DO: wrong column names