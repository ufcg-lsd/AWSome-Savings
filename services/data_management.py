import math
import csv
from .calculator import InstancePrices

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

                # coloca os tipos de instância em um dicionário
                for i in range(1, len(header)):
                    instance_type = header[i].strip('\n').strip('"')
                    demand[instance_type] = []
                
                # itera sobre o arquivo para formar as demandas de cada tipo
                while True:
                    line = file.readline()
                    if not line:
                        break
                    line = line.split(',')

                    for i in range(1, len(line)):
                        instance_type = header[i].strip('\n').strip('"')
                        demand[instance_type].append(int(line[i]))
        return demand
    
    def write_output(self, output, output_path):
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
                l = [t * 3600]
                for family in families:
                    l.append(market_costs[family][t])
                l.append(market)
                writer.writerow(l)

        output_file.close()
        
    def write_output_summarize(self, output, output_path):
        output_file = open(output_path, 'w')
        writer = csv.writer(output_file)

        writer.writerow(['timestamp', 'OnDemand', 'RAllUpfront', 'RPartialUpfront', 'RNoUpfront', 'AllMarkets'])
        for t in range(len(output['OnDemand'])):
            l = [t * 3600, output['OnDemand'][t], output['RAllUpfront'][t], output['RPartialUpfront'][t], output['RNoUpfront'][t]]
            l.append(sum(l[1:]))
            writer.writerow(l)

        output_file.close()

    def slice_classic_data(self, demand, proportions):
        method = proportions[0].lower()
        types = [{}, {}, {}, {}]
        if method == 'proportion':
            for instace_type, instance_demand in demand.items():
                for quantity in instance_demand:
                    value = quantity
                    for index in range(len(types)):
                        percent = math.ceil(value * proportions[index + 1])
                        if instace_type in types[index]:
                            types[index][instace_type].append(percent)
                            value -= percent
                        else:
                            types[index][instace_type] = [percent]
                            value -= percent
        elif method == 'absolute':
            print("To-do")
        return types
