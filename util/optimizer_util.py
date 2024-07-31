""" Converts the input to the optimizer format
"""

import csv
import os
import time
import subprocess

RES_DURATION = 8760
TIME_WAITING_RESULTS = 30

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

def write_allocation(raw_path, family):
    if not os.path.isfile(f'{raw_path}/allocation.csv'):
        os.system(f'cp {raw_path}/{family}/allocation.csv {raw_path}/allocation.csv')
    else:
        new_lines = []
        with open(f'{raw_path}/allocation.csv', 'r') as old, \
             open(f'{raw_path}/{family}/allocation.csv', 'r') as new:
            
            new_reader = [line for line in csv.reader(new)]
            old_reader = [line for line in csv.reader(old)]
            
            for i in range(len(old_reader)):
                new_lines.append(old_reader[i] + new_reader[i][2::])

        with open(f'{raw_path}/allocation.csv', 'w') as old:
            writer = csv.writer(old)
            writer.writerows(new_lines)

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

            write_allocation(f"{playpen}/raw/", family)