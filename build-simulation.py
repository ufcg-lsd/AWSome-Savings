"""Generates the input and output for aws_model.

Reads the files with the values for the simulation and converts the data to the format that the
aws_model module receives. Calls aws_model to build and run the simulation and generates output 
files with the results.

It receives 3 csv files:
- input: values for every market for every instance used in the simulation;
- input_sp: values for savings plan for every instance used in the simulation;
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
    raw_input = pd.read_csv(sys.argv[1])
    raw_sp_input = pd.read_csv(sys.argv[2])
    raw_demand = pd.read_csv(sys.argv[3])

    validate_input(raw_input)
    
    instances = list(raw_input['instance'].value_counts().index)
    instances.sort()
    
    validate_sp_input(raw_sp_input, instances)
    validate_demand(raw_demand, instances)

    resultCost = open('data/resultCost.csv', 'w')
    writerCost = csv.writer(resultCost)
    writerCost.writerow(['instance','total_cost'])

    input_data = []
    input_sp = []
    total_demand = []

    for instance in instances:
        line_sp = raw_sp_input[raw_sp_input['instance'] == instance]
        input_sp.append(line_sp['p_hr'])
        instance_input = []
        market_names = []

        for i in range(len(raw_input)):
            line = raw_input.iloc[i]
            if line['instance'] == instance:
                instance_input.append([line['p_hr'],line['p_up'], line['y']])
                market_names.append(line['market_name'])
        input_data.append(instance_input)

        instance_demand = raw_demand[instance].values.tolist()
        total_demand.append(instance_demand)

    t = len(total_demand[0])
    y_sp = (raw_sp_input.iloc[0])['y']

    result = optimize_model(t, total_demand, input_data, input_sp, y_sp)
    cost = result[0]
    values = generate_list(result[1], t, len(instances), len(market_names))

    writerCost.writerow(['all', cost])

    outputSavingsPlan(values, t, y_sp, writerCost)
    outputInstances(values, t, instances, market_names, input_data, writerCost)

# the validations could be in another file?
def validate_input(raw_input):
    validate_columns('input.csv', raw_input, ['instance', 'market_name', 'p_hr', 'p_up', 'y'])
    
    instances = list(raw_input['instance'].value_counts().index)
    instances.sort()
    validate_markets(raw_input, instances)

def validate_columns(file_name, data_frame, names):
    if list(data_frame.columns) != names:
        raise Exception('The column names in ' + file_name +  ' are incorrect.')

def validate_markets(raw_input, instances):
    #All instances should have the same markets
    instance_input = raw_input[raw_input['instance'] == instances[0]]
    markets = list(instance_input.loc[:,'market_name'])
    markets.sort()
    previous_markets = markets
    
    for instance in instances:
        instance_input = raw_input[raw_input['instance'] == instance]
        markets = list(instance_input.loc[:,'market_name'])
        markets.sort()
        if markets != previous_markets:
            raise Exception('Not all instances have the same market names.')
        previous_markets = markets

#sp means savings plan
def validate_sp_input(raw_sp_input, instances):
    validate_columns('input_sp.csv', raw_sp_input, ['instance', 'p_hr', 'y'])
    validate_sp_instances(raw_sp_input, instances)
    validate_sp_durations(raw_sp_input)

def validate_sp_instances(raw_sp_input, instances):
    #The instances in savings plan should be the same as the other markets
    sp_instances = list(raw_sp_input.loc[:,'instance'])
    sp_instances.sort()

    if instances != sp_instances:
        raise Exception('The instances names in input.csv and input_sp.csv are not the same.')

def validate_sp_durations(raw_sp_input):
    #All savings plan durations should be the same
    sp_durations = list(raw_sp_input['y'].value_counts().index)
    if len(sp_durations) != 1:
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
def outputInstances(values, t, instance_names, market_names, input_data, writerCost): #is it possible to calcule the savings plan cost of each instance?

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
            im_values = input_data[i_instance][i_market]
            cr_im = im_values[0] * im_values[2] + im_values[1]

            for i_time in range(t):
                active = values[i_time][i_instance + 1][i_market + 1][0]
                reserves = values[i_time][i_instance + 1][i_market + 1][1]
                writer.writerow([instance_names[i_instance], market_names[i_market], active, reserves])

                cost += reserves * cr_im

        writerCost.writerow([instance_names[i_instance], cost])        
        output.close()

# Generates total_purchases_savings_plan and the savings plan value in resultCost
def outputSavingsPlan(values, t, y_sp, writerCost):
    output = open('total_purchases_savings_plan.csv', 'w')
    writer = csv.writer(output)
    writer.writerow(['market', 'value_active', 'value_reserves'])
    cost = 0

    for i_time in range(t):
        values_sp = values[i_time][0][0]
        cost += values_sp[1] * y_sp
        writer.writerow(['savings_plan', values_sp[0], values_sp[1]])

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