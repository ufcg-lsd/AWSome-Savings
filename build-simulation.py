import csv
import pandas as pd
from aws_model import optimize_model

# the validations could be in another file?
def validate_input(raw_input, raw_sp_input, raw_demand):
    validate_column_names(raw_input, raw_sp_input, raw_demand)
    validate_savings_plan(raw_sp_input)

    input_instances = list(raw_input['instance'].value_counts().index)
    sp_input_instances = list(raw_sp_input.loc[:,'instance'])
    input_instances.sort
    sp_input_instances.sort

    validate_instance_names(input_instances, sp_input_instances, raw_demand)
    validate_markets(raw_input, input_instances)

    #other validations (that may cause performance overhead):
    #no blank or null values
    #all the demand values and the reserve durations must be integers

def validate_column_names(raw_input, raw_sp_input, raw_demand):
    if list(raw_input.columns) != ['instance', 'market_name', 'p_hr', 'p_up', 'y']:
        raise Exception('Column names in input.csv are incorrect.')
    if list(raw_sp_input.columns) != ['instance', 'p_hr', 'y']:
        raise Exception('Column names in input_sp.csv are incorrect.')
    if raw_demand.columns[0] != 'Hour': #could i just correct in the code?
        raise Exception('The first column name in the demand file is incorrect.')

def validate_instance_names(input_instances, sp_input_instances, raw_demand):
    #the instance names in both input files should be the same

    if input_instances != sp_input_instances:
        raise Exception('The instances names in input.csv and input_sp.csv are not the same.')
    
    #the demand should contain all the instances passed on the input
    demand_col = list(raw_demand.columns)
    for instance in input_instances:
        if instance not in demand_col:
            raise Exception('The instance ' + instance + ' is not on the demand file.')

def validate_markets(raw_input, input_instances):
    #All instances should have the same markets
    instance_input = raw_input[raw_input['instance'] == input_instances[0]]
    market_names = list(instance_input.loc[:,'market_name'])
    market_names.sort
    previous_market_names = market_names
    
    for instance in input_instances:
        instance_input = raw_input[raw_input['instance'] == instance]
        market_names = list(instance_input.loc[:,'market_name'])
        market_names.sort
        if market_names != previous_market_names:
            raise Exception('Not all instances have the same market names.')
        previous_market_names = market_names

def validate_savings_plan(raw_sp_input):
    #All savings plan durations should be the same
    sp_durations = list(raw_sp_input['y'].value_counts().index)
    if len(sp_durations) != 1:
        raise Exception('All instances must have the same savings plan duration.')

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

raw_input = pd.read_csv('data/input.csv')
raw_sp_input = pd.read_csv('data/input_sp.csv')
instances = raw_input['instance'].value_counts()

raw_demand = pd.read_csv('data/TOTAL_demand.csv')

validate_input(raw_input, raw_sp_input, raw_demand)

resultCost = open('data/resultCost.csv', 'w')
writerCost = csv.writer(resultCost)
writerCost.writerow(['instance','total_cost'])

input_data = []
input_sp = []
total_demand = []
instance_names = []

for instance in instances.index:
    line_sp = raw_sp_input[raw_sp_input['instance'] == instance]
    input_sp.append(line_sp['p_hr'])
    instance_input = []
    market_names = []
    instance_names.append(instance)

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
values = generate_list(result[1], t, len(instance_names), len(market_names))

writerCost.writerow(['all', cost])

outputSavingsPlan(values, t, y_sp, writerCost)
outputInstances(values, t, instance_names, market_names, input_data, writerCost)