"""Generates the input and output for aws_model.

Reads the files with the values for the simulation and converts the data to the format that the
aws_model module receives. Calls aws_model to build and run the simulation and generates output 
files with the results.

It receives 3 csv files:
- on_demand_config: values for the on demand market for every instance used in the simulation;
- savings_plan_config: values for savings plan for every instance used in the simulation;
- total_demand: demand for all instances (including instances not used in the simulation).
There are examples of thoses files in the data folder.

It generates the following csv files:
- result_cost: the total cost of the simulation, the cost for every instance and the total 
    savings plan cost;
- total_purchases_savings_plan: for every hour, the active value and the value reserved 
    for savings plan;
- total_purchases_{instance_name}: one file for every instance. It has, for every hour 
    and every market type (including savings plan), the number of active instances and 
    the number of reserves made.
"""

import sys
import logging
import pandas as pd
import validations
from aws_model import optimize_model

def main():
    logging.basicConfig(filename='aws_model.log', format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Getting input data')
    on_demand_config = pd.read_csv(sys.argv[1])
    savings_plan_config = pd.read_csv(sys.argv[2])
    raw_demand = pd.read_csv(sys.argv[3])

    logging.info('Validating input data')
    validations.validate_on_demand_config(on_demand_config)

    instances = list(on_demand_config['instance'].value_counts().index)
    instances.sort()
    
    validations.validate_savings_plan_config(savings_plan_config, instances)
    validations.validate_demand(raw_demand, instances)
    
    logging.info('Transforming input data')
    savings_plan_data = []
    on_demand_data = []
    total_demand = []

    for instance in instances:
        line_savings_plan = savings_plan_config[savings_plan_config['instance'] == instance]
        savings_plan_data.append(line_savings_plan['hourly_price'])
        instance_data = []
        market_names = ['on_demand']

        line_on_demand = on_demand_config[on_demand_config['instance'] == instance]
        on_demand_data.append(float(line_on_demand['hourly_price']))

        instance_demand = raw_demand[instance].values.tolist()
        total_demand.append(instance_demand)

    t = len(total_demand[0])
    savings_plan_duration = (savings_plan_config.iloc[0])['duration']

    logging.info('Start building the model')
    result = optimize_model(t, total_demand, on_demand_data, savings_plan_data, savings_plan_duration)
    
    if result == []: raise Exception('The problem does not have an optimal solution.')
    
    total_cost = result[0]
    values = generate_list(result[1], t, len(instances), len(market_names))

    logging.info('Generating output')
    #generates the output files
    generate_result_cost(total_cost, values, t, instances, market_names, on_demand_data, savings_plan_duration)
    
    hour_index = raw_demand['hour'].values.tolist()
    generate_total_purchases_savings_plan(values, hour_index)
    generate_total_purchases(values, hour_index, instances, market_names)
    logging.info('Finished')

def generate_result_cost(total_cost, values, t, instance_names, market_names, on_demand_data, savings_plan_duration):
    result_cost = pd.DataFrame({'instance': ['all'], 'total_cost': [total_cost]})

    #calculating savings plan total cost
    savings_plan_cost = 0
    for i_time in range(t):
        savings_plan_cost += values[i_time][0][0][1] * savings_plan_duration #value of savings plan reserves made * savings plan duration 
    
    new_line = pd.DataFrame({'instance': ['savings_plan'], 'total_cost': [savings_plan_cost]})
    result_cost = pd.concat([result_cost, new_line])

    #calculating every instance total cost
    #this cost does not considers savings plan cost for the instance
    for i_instance in range(len(instance_names)):
        instance_cost = 0
        
        for i_market in range(len(market_names)):
            reserve_cost_im = on_demand_data[i_instance] #the only market is on demand

            for i_time in range(t):
                reserves = values[i_time][i_instance + 1][i_market + 1][1]
                instance_cost += reserves * reserve_cost_im
        
        new_line = pd.DataFrame({'instance': [instance_names[i_instance]], 'total_cost': [instance_cost]})
        result_cost = pd.concat([result_cost, new_line])

    result_cost.to_csv('result_cost.csv', index=False)

def generate_total_purchases_savings_plan(values, hour_index):
    total_purchases_savings_plan = pd.DataFrame(columns=['hour', 'market', 'value_active', 'value_reserves'])

    for i_time in range(len(hour_index)):
        values_savings_plan = values[i_time][0][0]
        new_line = pd.DataFrame({'hour': [int(hour_index[i_time])],
                                 'market': ['savings_plan'], 
                                 'value_active': [values_savings_plan[0]], 
                                 'value_reserves': [values_savings_plan[1]]})
        total_purchases_savings_plan = pd.concat([total_purchases_savings_plan, new_line])
    
    total_purchases_savings_plan.to_csv('total_purchases_savings_plan.csv', index=False)

# Generates total_purchases for every instance
def generate_total_purchases(values, hour_index, instance_names, market_names):

    for i_instance in range(len(instance_names)):
        total_purchases = pd.DataFrame(columns=['hour', 'instance_type', 'market', 'count_active', 'count_reserves'])
        instance_name = instance_names[i_instance]

        #Savings plan
        for i_time in range(len(hour_index)):
            active = values[i_time][i_instance + 1][0][0]
            new_line = pd.DataFrame({'hour': [int(hour_index[i_time])],
                                     'instance_type': [instance_name], 'market': ['savings_plan'],
                                     'count_active': [active],'count_reserves': [0]})
            total_purchases = pd.concat([total_purchases, new_line])
                    
        #Other markets
        for i_market in range(len(market_names)):
            for i_time in range(len(hour_index)):
                active = values[i_time][i_instance + 1][i_market + 1][0]
                reserves = values[i_time][i_instance + 1][i_market + 1][1]
                new_line = pd.DataFrame({'hour': [int(hour_index[i_time])],
                                         'instance_type': [instance_name], 'market': [market_names[i_market]],
                                         'count_active': [active],'count_reserves': [reserves]})
                total_purchases = pd.concat([total_purchases, new_line])
        
        total_purchases.to_csv('total_purchases_' + instance_name + '.csv', index=False)

def generate_list(values, t, num_instances, num_markets):
    index = 0
    list = []
    for i_time in range(t):
        list_time = []
        list_time.append([[values[index], values[index + 1]]])
        index += 2
        for i_instance in range(num_instances):
            list_instance = []
            list_instance.append([values[index]])
            index += 1
            for i_market in range(num_markets):
                list_instance.append([values[index], values[index + 1]])
                index += 2
            list_time.append(list_instance)
        list.append(list_time)
    return list

if __name__ == "__main__":
    main()