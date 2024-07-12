""" Converts the input to the optimizer format
"""

import csv
import os
import time
import subprocess

RES_DURATION = 8760
TIME_WAITING_RESULTS = 30
#INSTANCE_TYPES = ['m5.12xlarge','m5.16xlarge','m5.2xlarge','m5.4xlarge','m5.8xlarge','m5.large','m5.xlarge'] #change here the group you want

def generate_optimizer_input(demand_path, prices_path, playpen):

    # read demand to dictionary
    demand = read_demand(demand_path)
    timestamp = {'timestamp': demand['timestamp']}
    demand.pop('timestamp')

    # get demand dictionaries
    families = get_families(demand)

    for family in families:
        # create family directory in /tmp/costplanner_playpen/optimizer/exec/families/family
        family_directory = f'{playpen}/input/{family}'
        os.makedirs(family_directory, exist_ok=True)

        # get instance types for current family and create header
        instance_types = families[family]
        header = ['hour'] + instance_types

        # open the demand file in the family directory
        demand_file = open(f'{family_directory}/demand.csv', 'w')
        demand_writer = csv.writer(demand_file)
        demand_writer.writerow(header)

        max_t = len(demand[instance_types[0]])

        for t in range(max_t):
            line = [t]
            for instance_type in instance_types:
                line.append(demand[instance_type][t])

            demand_writer.writerow(line)
        
        demand_file.close()

        convert_prices(prices_path, family, instance_types, family_directory)

    return timestamp

def convert_prices(price_path, family, instance_types, family_directory):
    sp_file = open(f'{family_directory}/savings_plan_config.csv', 'w')
    sp_writer = csv.writer(sp_file)
    sp_writer.writerow(['instance','RNoUpfront1YM','duration'])

    od_file = open(f'{family_directory}/on_demand_config.csv', 'w')
    od_writer = csv.writer(od_file)
    od_writer.writerow(['instance','hourly_price'])

    with open(price_path, mode='r') as file:
            header = file.readline().split(',')
            
            while True:
                line = file.readline()
                if not line:
                    break
                line = line.split(',')
                
                instance_type = line[0]
                on_demand_hour = float(line[1])

                # only NO-UPFRONT is considered
                # TODO: add reserve markets as arguments in optimization
                #up_all_upfront = float(line[2])
                #up_partial_upfront = float(line[3])
                #hr_partial_upfront = float(line[4])

                hr_no_upfront = float(line[5])

                if instance_type in instance_types:
                    sp_writer.writerow([instance_type, hr_no_upfront, RES_DURATION])
                    od_writer.writerow([instance_type, on_demand_hour])

    sp_file.close()
    od_file.close()

def read_demand(demand_path):
    demand = {}
    
    with open(demand_path, mode='r') as file:
        header = file.readline().split(',')

        while True:
            line = file.readline()

            if not line:
                break

            line_elements = line.split(',')

            for i in range(len(header)):
                flavor = header[i].rstrip()

                if flavor not in list(demand.keys()):
                    demand[flavor] = []

                demand[flavor].append(int(line_elements[i]))
                
    return demand

def get_families(demand):
    families = {}
    for instance_type in demand:
        if len(instance_type.split('.')) == 1:
            family = instance_type
        else: 
            family, type = instance_type.split('.')
        if family in families:
            families[family].append(instance_type)
        else:
            families[family] = [instance_type]
    return families

def filter_optimization_ondemand(path_to_filter, prices, current_result):
    with open(path_to_filter, 'r') as demand_file:
        # fill the dictionary of prices if it doesn't exists
        all_rows = demand_file.readlines()
        rows_ondemand = int((len(all_rows) - 1)/2)
        for market in current_result.keys():
            if len(current_result[market]) == 0:
                current_result[market] = [0 for _ in range(rows_ondemand)]
        
        # read the allocation and put in a variable
        demand_reader = csv.reader(all_rows)
        # Ignore the first line(header)
        next(demand_reader, None)
        index = 0
        for row in demand_reader:
            if row[2] == 'on_demand':
                current_result['OnDemand'][index] += float(row[4]) * prices[row[1]].on_demand
                index += 1

def filter_optimization_savings_plan(path_to_filter, current_result):
    with open(path_to_filter, 'r') as demand_file:
        demand_reader = csv.reader(demand_file)
        # Ignore the first line(header)
        next(demand_reader, None)
        # The list comprehension below remove the 4th column (count_active)
        for index, row in enumerate(demand_reader):
            current_result['RNoUpfront'][index] += float(row[3])

def run_optimizations(playpen):
    # Function to run optimization for a family
    for family in os.listdir(f'{playpen}/input'):
        if not family.endswith(".csv"):
            os.makedirs(f'{playpen}/raw/{family}', exist_ok=True)
            optimization_args = [f'/calculation/optimizer/build/opt.elf', 
                            f'{playpen}/input/{family}/on_demand_config.csv',
                            f'{playpen}/input/{family}/savings_plan_config.csv',
                            f'{playpen}/input/{family}/demand.csv',
                            f'{playpen}/raw/{family}']
            
            optimization = subprocess.Popen(optimization_args)
            optimization.wait()

            while not os.path.isfile(f'{playpen}/raw/{family}/result_cost.csv'):
                time.sleep(TIME_WAITING_RESULTS)

def prepare_output_dict(playpen, prices):
    result = {'OnDemand': [], 'RAllUpfront': [], 'RPartialUpfront': [], 'RNoUpfront': []}

    # Iterates over the families directory
    for family in os.listdir(f"{playpen}/raw"):
        demand_directory = os.listdir(f"{playpen}/raw/{family}/")
        # Iterates over the demand output of a family and filter the columns
        for demand_file in demand_directory:
            file_type = demand_file.split('.')[0]
            if file_type == f"total_purchases_{family}":
                filter_optimization_ondemand(f"{playpen}/raw/{family}/{demand_file}", prices, result)
                
        filter_optimization_savings_plan(f"{playpen}/raw/{family}/total_purchases_savings_plan.csv", result)
    return result