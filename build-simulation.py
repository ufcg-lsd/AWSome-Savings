"""Generates the input and output for aws_model.

Reads the files with the values for the simulation and converts the data to the format that the
aws_model module receives. Calls aws_model to build and run the simulation and generates output 
files with the results.

It receives 4 csv files:
- on_demand_config: values for the on demand market for every instance used in the simulation;
- reserves_config: values for the reserve markets for every instance used in the simulation;
- savings_plan_config: values for savings plan for every instance used in the simulation;
- TOTAL_demand: demand for all instances (including instances not used in the simulation).
There are examples of thoses files in the data folder.

It generates the following csv files:
- resultCost: the total cost of the simulation, the cost for every instance and the total 
    savings plan cost;
- total_purchases_savings_plan: for every hour, the active value and the value reserved 
    for savings plan;
- total_purchases_{instance_name}: one file for every instance. It has, for every hour 
    and every market type (including savings plan), the number of active instances and 
    the number of reserves made.
"""

import csv
import sys
import pandas as pd
from aws_model import optimize_model

def main():
    on_demand_config = pd.read_csv(sys.argv[1])
    reserves_config = pd.read_csv(sys.argv[2])
    savings_plan_config = pd.read_csv(sys.argv[3])
    raw_demand = pd.read_csv(sys.argv[4])

    validate_on_demand_config(on_demand_config)
    
    instances = list(on_demand_config['instance'].value_counts().index)
    instances.sort()
    
    validate_reserves_config(reserves_config, instances)
    validate_savings_plan_config(savings_plan_config, instances)
    validate_demand(raw_demand, instances)

    resultCost = open('data/resultCost.csv', 'w')
    writerCost = csv.writer(resultCost)
    writerCost.writerow(['instance','total_cost'])

    markets_data = []
    savings_plan_data = []
    total_demand = []

    for instance in instances:
        line_savings_plan = savings_plan_config[savings_plan_config['instance'] == instance]
        savings_plan_data.append(line_savings_plan['p_hr'])
        instance_data = []
        market_names = ['on_demand']

        line_on_demand = on_demand_config[on_demand_config['instance'] == instance]
        instance_data.append([float(line_on_demand['p_hr']), 0, 1])

        for i in range(len(reserves_config)):
            line = reserves_config.iloc[i]
            if line['instance'] == instance:
                instance_data.append([line['p_hr'],line['p_up'], line['y']])
                market_names.append(line['market_name'])
        markets_data.append(instance_data)

        instance_demand = raw_demand[instance].values.tolist()
        total_demand.append(instance_demand)

    t = len(total_demand[0])
    savings_plan_duration = (savings_plan_config.iloc[0])['y']

    result = optimize_model(t, total_demand, markets_data, savings_plan_data, savings_plan_duration)
    cost = result[0]
    values = generate_list(result[1], t, len(instances), len(market_names))

    writerCost.writerow(['all', cost])

    outputSavingsPlan(values, t, savings_plan_duration, writerCost)
    outputInstances(values, t, instances, market_names, markets_data, writerCost)

# the validations could be in another file?
def validate_on_demand_config(on_demand_config):
    validate_columns('on_demand_config', on_demand_config, ['instance', 'p_hr'])

def validate_columns(file_name, data_frame, names):
    if list(data_frame.columns) != names:
        raise Exception('The column names in ' + file_name +  ' are incorrect.')

def validate_reserves_config(reserves_config, instances):
    validate_columns('reserves_config', reserves_config, ['instance', 'market_name', 'p_hr', 'p_up', 'y'])
    validate_instances_names('reserves_config', reserves_config, instances)
    validate_reserves_markets(reserves_config, instances)

def validate_instances_names(file_name, data_frame, instances):
    #Checks if the instance names in the data_frame are the same as in the other files
    file_instances = list(data_frame.loc[:,'instance'])
    file_instances.sort()

    if instances != file_instances:
        raise Exception('The instances names in on_demand_config and ' + file_name + ' are not the same.')

def validate_reserves_markets(reserves_config, instances):
    #All instances should have the same reserve markets
    instance_line = reserves_config[reserves_config['instance'] == instances[0]]
    markets = list(instance_line.loc[:,'market_name'])
    markets.sort()
    previous_markets = markets
    
    for instance in instances:
        instance_line = reserves_config[reserves_config['instance'] == instance]
        markets = list(instance_line.loc[:,'market_name'])
        markets.sort()
        if markets != previous_markets:
            raise Exception('Not all instances have the same reserve market names.')
        previous_markets = markets

def validate_savings_plan_config(savings_plan_config, instances):
    validate_columns('savings_plan_config', savings_plan_config, ['instance', 'p_hr', 'y'])
    validate_instances_names('savings_plan_config', savings_plan_config, instances)
    validate_savings_plan_durations(savings_plan_config)

def validate_savings_plan_durations(savings_plan_config):
    #All savings plan durations should be the same
    savings_plan_durations = list(savings_plan_config['y'].value_counts().index)
    if len(savings_plan_durations) != 1:
        raise Exception('All instances must have the same savings plan duration.')

def validate_demand(raw_demand, instances):
    if raw_demand.columns[0] != 'Hour': #could i just correct in the code?
        raise Exception('The first column name in the demand file is incorrect.')
    
    validate_demand_instances(raw_demand, instances)

def validate_demand_instances(raw_demand, instances):
    #the demand should contain all the instances passed on the input
    demand_col = list(raw_demand.columns)
    for instance in instances:
        if instance not in demand_col:
            raise Exception('The instance ' + instance + ' is not on the demand file.') 

# Generates total_purchases for every instance and the instance values in resultCost
def outputInstances(values, t, instance_names, market_names, markets_data, writerCost): #is it possible to calcule the savings plan cost of each instance?

    for i_instance in range(len(instance_names)):
        cost = 0

        output = open('total_purchases_' + instance_names[i_instance] + '.csv', 'w')
        writer = csv.writer(output)
        writer.writerow(['instanceType', 'market', 'count_active', 'count_reserves'])

        #Savings plan
        for i_time in range(t):
            active = values[i_time][i_instance + 1][0][0]
            writer.writerow([instance_names[i_instance], 'savings_plan', active, 0])

            #the individual instance cost in the output does not considers savings plan cost
                
        #Other markets
        for i_market in range(len(market_names)):
            im_values = markets_data[i_instance][i_market]
            cr_im = im_values[0] * im_values[2] + im_values[1]

            for i_time in range(t):
                active = values[i_time][i_instance + 1][i_market + 1][0]
                reserves = values[i_time][i_instance + 1][i_market + 1][1]
                writer.writerow([instance_names[i_instance], market_names[i_market], active, reserves])

                cost += reserves * cr_im

        writerCost.writerow([instance_names[i_instance], cost])        
        output.close()

# Generates total_purchases_savings_plan and the savings plan value in resultCost
def outputSavingsPlan(values, t, savings_plan_duration, writerCost):
    output = open('total_purchases_savings_plan.csv', 'w')
    writer = csv.writer(output)
    writer.writerow(['market', 'value_active', 'value_reserves'])
    cost = 0

    for i_time in range(t):
        values_savings_plan = values[i_time][0][0]
        cost += values_savings_plan[1] * savings_plan_duration
        writer.writerow(['savings_plan', values_savings_plan[0], values_savings_plan[1]])

    writerCost.writerow(['savings_plan', cost])

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