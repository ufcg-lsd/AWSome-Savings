""" Tests for the model.
"""

import unittest
import pandas as pd
import os

class TestAWSModel(unittest.TestCase):

    def tearDown(self):
        os.remove('on_demand_config.csv')
        os.remove('reserves_config.csv')
        os.remove('savings_plan_config.csv')
        os.remove('TOTAL_demand.csv')

    # def test_ex(self):
    #     on_demand_config = {'instance': [],
    #                         'p_hr': []}

    #     on_demand_df = pd.DataFrame(on_demand_config)
    #     on_demand_df.to_csv('on_demand_config.csv', index=False)

    #     reserves_config = {'instance': [],
    #                         'market_name': [],
    #                         'p_hr': [],
    #                         'p_up': [],
    #                         'y': []}

    #     reserves_df = pd.DataFrame(reserves_config)
    #     reserves_df.to_csv('reserves_config.csv', index=False)

    #     savings_plan_config = {'instance': [],
    #                             'p_hr': [],
    #                             'y': []}

    #     savings_plan_df = pd.DataFrame(savings_plan_config)
    #     savings_plan_df.to_csv('savings_plan_config.csv', index=False)

    #     demand = {'Hour': []}

    #     demand_df = pd.DataFrame(demand)
    #     demand_df.to_csv('TOTAL_demand.csv', index=False)

    #     os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

    #     #only checks the total cost
    #     result_cost = pd.read_csv('../data/resultCost.csv')
    #     actual_cost = result_cost.loc[0, 'total_cost']
    #     self.assertEqual(actual_cost, 0)

    #1
    def test_savings_plan(self):
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [1, 1],
                            'p_up': [0, 0],
                            'y': [4, 4]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [1, 1],
                                'y': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4],
                  'a': [10, 10, 5, 5],
                  'b': [5, 5, 10, 10]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 60)

    #2
    def test_on_demand_reserved(self):
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [1, 1],
                            'p_up': [0, 0],
                            'y': [5, 5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [1.1, 1.1],
                                'y': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 20, 20, 20, 20, 30],
                  'b': [10, 20, 20, 20, 20, 30]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 280)

    #3
    def test_savings_plan_on_demand(self):
        #very similar to the previous test, test_on_demand_reserved
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [1.1, 1.1],
                            'p_up': [0, 0],
                            'y': [5, 5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [1, 1],
                                'y': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 20, 20, 20, 20, 30],
                  'b': [10, 20, 20, 20, 20, 30]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 280)

    #4
    def test_savings_plan_reserved(self):
        #very similar to the previous tests, test_on_demand_reserved and test_savings_plan_on_demand
        #in this test, there is no difference in cost in allocating instances for savings plan or reserved
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [2, 2]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [1, 1],
                            'p_up': [0, 0],
                            'y': [5, 5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [1, 1],
                                'y': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 20, 20, 20, 20, 30],
                  'b': [10, 20, 20, 20, 20, 30]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 280)

    #5
    def test_savings_plan_in_the_future(self):
        #the savings plan reserve goes beyond the simulation period
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [20, 20]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [20, 20],
                            'p_up': [0, 0],
                            'y': [4, 4]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [1, 1],
                                'y': [5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4],
                  'a': [10, 10, 5, 5],
                  'b': [5, 5, 10, 10]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 75)

    #6
    def test_savings_plan_reserve_different_durations(self):
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [4, 4]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [1.5, 1.5],
                            'p_up': [0, 0],
                            'y': [2, 2]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [1, 1],
                                'y': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 7, 6, 12, 5, 5], 
                  'b': [5, 8, 9, 3, 4, 4]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 87)

    #7
    def test_savings_plan_reserve_different_durations_2(self):
        #similar to 6, but uses only savings plan
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [4, 4]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [2.1, 2.1],
                            'p_up': [0, 0],
                            'y': [2, 2]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [1, 1],
                                'y': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 7, 6, 12, 5, 5], 
                  'b': [5, 8, 9, 3, 4, 4]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 96)

    #8
    def test_savings_plan_reserve_on_demand(self):
        #similar to 6
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [2.5, 2.5]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [1.5, 1.5],
                            'p_up': [0, 0],
                            'y': [2, 2]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [1, 1],
                                'y': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 7, 6, 12, 5, 6], 
                  'b': [5, 8, 9, 3, 4, 7]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 97)

    #9
    def test_savings_plan_different_prices(self):
        #In this test, we got the expected cost from running the tool. We checked that it respect the rules. 
        on_demand_config = {'instance': ['a', 'b'],
                            'p_hr': [4, 4]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b'],
                            'market_name': ['reserved', 'reserved'],
                            'p_hr': [20, 20],
                            'p_up': [0, 0],
                            'y': [4, 4]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b'],
                                'p_hr': [3, 1],
                                'y': [4, 4]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4, 5, 6],
                  'a': [3, 4, 6, 0, 0, 0], 
                  'b': [0, 0, 0, 15, 20, 23]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(actual_cost, 120)

    #10
    def test_randon(self):
        #In this test, we got the expected cost from running the tool. We checked that it respect the rules. 
        on_demand_config = {'instance': ['a', 'b', 'c'],
                            'p_hr': [3, 7, 1.5]}

        on_demand_df = pd.DataFrame(on_demand_config)
        on_demand_df.to_csv('on_demand_config.csv', index=False)

        reserves_config = {'instance': ['a', 'b', 'c'],
                            'market_name': ['reserved', 'reserved', 'reserved'],
                            'p_hr': [0.8, 1.5, 0.4],
                            'p_up': [0, 0, 0],
                            'y': [5, 5, 5]}

        reserves_df = pd.DataFrame(reserves_config)
        reserves_df.to_csv('reserves_config.csv', index=False)

        savings_plan_config = {'instance': ['a', 'b', 'c'],
                                'p_hr': [1, 2, 0.5],
                                'y': [5, 5, 5]}

        savings_plan_df = pd.DataFrame(savings_plan_config)
        savings_plan_df.to_csv('savings_plan_config.csv', index=False)

        demand = {'Hour': [1, 2, 3, 4, 5, 6],
                  'a': [10, 11, 9, 32, 3, 0],
                  'b': [3, 7, 4, 2, 9, 10], 
                  'c': [38, 24, 42, 2, 17, 13]}

        demand_df = pd.DataFrame(demand)
        demand_df.to_csv('TOTAL_demand.csv', index=False)

        os.system('cd .. && python3 build-simulation.py tests/on_demand_config.csv tests/reserves_config.csv tests/savings_plan_config.csv tests/TOTAL_demand.csv')

        #only checks the total cost
        result_cost = pd.read_csv('../data/resultCost.csv')
        actual_cost = result_cost.loc[0, 'total_cost']
        self.assertEqual(round(actual_cost), 244)


        #11 - test only one instance (3 markets)

        #12 - test more than one reserve market (all up, parcial up, no up, 1y, 3y)

        #tests invalid input