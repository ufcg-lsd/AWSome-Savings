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
    #     actual_cost = result_cost.loc[1, 'total_cost']
    #     self.assertEqual(actual_cost, 0)

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
        actual_cost = result_cost.loc[1, 'total_cost']
        self.assertEqual(actual_cost, 60)
