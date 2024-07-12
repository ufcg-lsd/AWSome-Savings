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

        self.safe_remove('tests/test_data/on_demand_config.csv')
        self.safe_remove('tests/test_data/savings_plan_config.csv')
        self.safe_remove('tests/test_data/total_demand.csv')
        self.safe_remove('result_cost.csv')
        self.safe_remove('total_purchases_savings_plan.csv')
        self.safe_remove('total_purchases_a.csv')
        self.safe_remove('total_purchases_b.csv')
        self.safe_remove('total_purchases_c.csv')

    #1
    def test_savings_plan(self):
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4],
                  'a': [10, 10, 5, 5],
                  'b': [5, 5, 10, 10]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        subprocess.run('./cpp/build/opt.elf tests/test_data/on_demand_config.csv tests/test_data/savings_plan_config.csv tests/test_data/total_demand.csv', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 60)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #2
    # on_demand e reserved

    #3
    def test_savings_plan_on_demand(self):
        #very similar to the previous test, test_on_demand_reserved
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 20, 20, 20, 20, 30],
                  'b': [10, 20, 20, 20, 20, 30]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        out = subprocess.run('./cpp/build/opt.elf tests/test_data/on_demand_config.csv tests/test_data/savings_plan_config.csv tests/test_data/total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 280)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #4
    # Savings plan ou reserva e on_demand

    #5
    def test_savings_plan_in_the_future(self):
        #the savings plan reserve goes beyond the simulation period
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [20, 20]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4],
                  'a': [10, 10, 5, 5],
                  'b': [5, 5, 10, 10]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        out = subprocess.run('./cpp/build/opt.elf tests/test_data/on_demand_config.csv tests/test_data/savings_plan_config.csv tests/test_data/total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 75)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #6
    # Savings_plan e reserva com diferentes durações

    #7
    def test_savings_plan_reserve_different_durations_2(self):
        #similar to 6, but uses only savings plan
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [4, 4]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [1, 1],
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 7, 6, 12, 5, 5], 
                  'b': [5, 8, 9, 3, 4, 4]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        out = subprocess.run('./cpp/build/opt.elf tests/test_data/on_demand_config.csv tests/test_data/savings_plan_config.csv tests/test_data/total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 96)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #8
    # reserva, savings plan e on_demand

    #9
    def test_savings_plan_different_prices(self):
        #In this test, we got the expected cost from running the tool. We checked that it respect the rules. 
        on_demand_config = {'instance': ['a', 'b'],
                            'hourly_price': [4, 4]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'hourly_price': [3, 1],
                                'duration': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [3, 4, 6, 0, 0, 0], 
                  'b': [0, 0, 0, 15, 20, 23]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        out = subprocess.run('./cpp/build/opt.elf tests/test_data/on_demand_config.csv tests/test_data/savings_plan_config.csv tests/test_data/total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 120)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")

    #10
    #aleatório

    #11
    def test_one_instance_type(self):
        on_demand_config = {'instance': ['a'],
                            'hourly_price': [2.2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a'],
                                'hourly_price': [1.2],
                                'duration': [2]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 15, 15, 10, 10, 10]} 

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        out = subprocess.run('./cpp/build/opt.elf tests/test_data/on_demand_config.csv tests/test_data/savings_plan_config.csv tests/test_data/total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

        try:
            #only checks the total cost
            result_cost = pd.read_csv('result_cost.csv')
            actual_cost = result_cost.loc[0, 'total_cost']
            self.assertEqual(actual_cost, 84)
        except FileNotFoundError:
            self.fail("The file result_cost.csv was not created.")
    
    #12
    #multiple_reserve_markets

    #tests checking validations

    #13
    def test_more_instances_total_demand(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [0.7, 0.9, 1.3],
                                'duration': [3, 3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'a': [1, 2, 0],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)
        
        out = subprocess.run('./cpp/build/opt.elf tests/test_data/on_demand_config.csv tests/test_data/savings_plan_config.csv tests/test_data/total_demand.csv', shell=True, stdout=subprocess.DEVNULL,
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
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [0.7, 0.9, 1.3],
                                'duration': [2, 3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'a': [1, 2, 0],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        with self.assertRaises(Exception):
            out = subprocess.run('./cpp/build/opt', shell=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT, check=True)

    #17
    def test_different_instances_savings_plan_config(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'c'],
                                'hourly_price': [0.7, 1.3],
                                'duration': [3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'a': [1, 2, 0],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        with self.assertRaises(Exception):
            out = subprocess.run('./cpp/build/opt', shell=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT, check=True)

    #18
    def test_different_instances_total_demand(self):
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'hourly_price': [1, 1.3, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('tests/test_data/on_demand_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'hourly_price': [0.7, 0.9, 1.3],
                                'duration': [3, 3, 3]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('tests/test_data/savings_plan_config.csv', index=False)

        demand = {'hour': [1, 2, 3],
                  'b': [4, 1, 2], 
                  'c': [0, 5, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('tests/test_data/total_demand.csv', index=False)

        with self.assertRaises(Exception):
            out = subprocess.run('./cpp/build/opt', shell=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT, check=True)  

        #TO DO: wrong column names
