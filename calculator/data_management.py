import math
import csv
from calculator.calculator import InstancePrices

class DataManagement:

    def __init__(self):
        pass

    def read_prices(self, prices_path):
        prices = {}
        with open(prices_path, mode='r') as file:
                header = file.readline().split(',')

                while True:
                    line = file.readline()
                    if not line:
                        break
                    line = line.split(',')

                    instance_type = line[0]
                    on_demand_hour = float(line[1])
                    up_all_upfront = float(line[2])
                    up_partial_upfront = float(line[3])
                    hr_partial_upfront = float(line[4])
                    hr_no_upfront = float(line[5])

                    prices[instance_type] = InstancePrices(on_demand_hour, up_all_upfront, up_partial_upfront, hr_partial_upfront, hr_no_upfront, up_all_upfront, up_partial_upfront, hr_partial_upfront, hr_no_upfront)
        return prices

    def read_demand(self, demand_path):
        demand = {}
        with open(demand_path, mode='r') as file:
                header = file.readline().split(',')

                # put the instacne types in a dictionary
                for i in range(0, len(header)):
                    instance_type = header[i].strip('\n').strip('"')
                    demand[instance_type] = []
                
                # iterates over the file to create the datasets of each type
                while True:
                    line = file.readline()
                    if not line:
                        break
                    line = line.split(',')

                    for i in range(0, len(line)):
                        instance_type = header[i].strip('\n').strip('"')
                        demand[instance_type].append(int(line[i]))

        timestamp = {'timestamp': demand['timestamp']}
        demand.pop('timestamp')

        return demand, timestamp

    def read_allocation(self, allocation_path):
        allocation = [{}, {}, {}, {}]

        with open(allocation_path, mode='r') as file:
                instance_names = file.readline().split(',')
                market = 0

                # iterates over the file to create the datasets of each type
                while True:
                    line = file.readline()
                    if not line:
                        break
                    line = line.split(',')

                    for i in range(2, len(line)):
                        instance_name = instance_names[i].strip("\n")
                        if instance_name in allocation[market]:
                            allocation[market][instance_name].append(int(line[i].strip("\n")))
                        else:
                            allocation[market][instance_name] = [int(line[i].strip("\n"))]

                    market = (market + 1) % 4

        return allocation

    def write_output(self, output, timestamp, output_path):
        output_file = open(output_path, 'w')
        writer = csv.writer(output_file)
        families = list(output['OnDemand'].keys())

        header = ['timestamp']
        for family in families:
            header.append(family)
        header.append('market')
        writer.writerow(header)

        for market in output:
            market_costs = output[market]
            for t in range(len(market_costs[families[0]])):
                l = [timestamp['timestamp'][t]]
                for family in families:
                    l.append(market_costs[family][t])
                l.append(market)
                writer.writerow(l)

        output_file.close()

    def write_output_summarize(self, output, timestamp, output_path):
        output_file = open(output_path, 'w')
        writer = csv.writer(output_file)

        writer.writerow(['timestamp', 'OnDemand', 'RAllUpfront', 'RPartialUpfront', 'RNoUpfront', 'AllMarkets'])
        for t in range(len(output['OnDemand'])):
            l = [timestamp['timestamp'][t], output['OnDemand'][t], output['RAllUpfront'][t], output['RPartialUpfront'][t], output['RNoUpfront'][t]]
            l.append(sum(l[1:]))
            writer.writerow(l)

        output_file.close()

    def allocate_demand(self, demand, proportions):
        method = proportions[0].lower()
        timestamp = {'timestamp': demand['timestamp']}
        demand.pop('timestamp')
        types = [{}, {}, {}, {}]
        if method == 'proportion':
            for instance_type, instance_demand in demand.items():
                maximum = max(instance_demand)
                allocated_no_up = math.floor(maximum * proportions[2])
                allocated_partial_up = math.floor(maximum * proportions[3])
                allocated_all_up = math.floor(maximum * proportions[4])
                on_demand_margin = allocated_no_up + allocated_partial_up + allocated_all_up
                for quantity in instance_demand:
                    total_instances = [0] * 4
                    total_instances[0] = max(0, quantity - on_demand_margin)
                    total_instances[1] = allocated_no_up
                    total_instances[2] = allocated_partial_up
                    total_instances[3] = allocated_all_up
                    for index, instances in enumerate(total_instances):
                        if instance_type in types[index]:
                            types[index][instance_type].append(instances)
                        else:
                            types[index][instance_type] = [instances]
        elif method == 'absolute':
            for instance_type, instance_demand in demand.items():
                for quantity in instance_demand:
                    value = quantity
                    for index in range(1, len(types)):
                        number = 0
                        if value - int(proportions[index + 1]) < 0:
                            number = value
                            value = 0
                        else:
                            number = int(proportions[index + 1])
                            value -= int(proportions[index + 1])
                        
                        if instance_type in types[index]:
                            types[index][instance_type].append(number)
                        else:
                            types[index][instance_type] = [number]
                    if instance_type in types[0]:
                        types[0][instance_type].append(value)
                    else:
                        types[0][instance_type] = [value]
        types.append(timestamp)
        return types