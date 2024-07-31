import math
from calculator.data_management import DataManagement

class Allocator:

    def __init__(self, demand, proportions):
        # Initialize the attributes of the Allocator class
        self.proportions = proportions
        self.types = [{}, {}, {}, {}]  # List of dictionaries to store allocation types
        self.demand = demand  # Demand by instance type
        self.datam = DataManagement()  # Instance of DataManagement to handle data operations

    def allocate_demand(self):
        # Method to allocate demand according to the method specified in proportions
        method = self.proportions[0].lower()  # First element of proportions defines the method
        if method == 'proportion':
            # Proportional allocation
            for instance_type, instance_demand in self.demand.items():
                maximum = max(instance_demand)  # Determine the maximum demand value
                allocated_no_up = math.floor(maximum * self.proportions[2])  # Calculate no upfront allocation
                allocated_partial_up = math.floor(maximum * self.proportions[3])  # Calculate partial upfront allocation
                allocated_all_up = math.floor(maximum * self.proportions[4])  # Calculate all upfront allocation
                on_demand_margin = allocated_no_up + allocated_partial_up + allocated_all_up  # On-demand margin
                for quantity in instance_demand:
                    total_instances = [0] * 4  # Initialize list for total instances
                    total_instances[0] = max(0, quantity - on_demand_margin)  # Calculate on-demand instances
                    total_instances[1] = allocated_no_up  # Assign no upfront instances
                    total_instances[2] = allocated_partial_up  # Assign partial upfront instances
                    total_instances[3] = allocated_all_up  # Assign all upfront instances
                    for index, instances in enumerate(total_instances):
                        if instance_type in self.types[index]:
                            self.types[index][instance_type].append(instances)  # Add instances to existing list
                        else:
                            self.types[index][instance_type] = [instances]  # Create new list of instances
        elif method == 'absolute':
            # Absolute allocation
            for instance_type, instance_demand in self.demand.items():
                for quantity in instance_demand:
                    value = quantity  # Initial demand value
                    for index in range(1, len(self.types)):
                        number = 0
                        if value - int(self.proportions[index + 1]) < 0:
                            number = value  # If value is less than proportion, use value
                            value = 0  # Set value to zero
                        else:
                            number = int(self.proportions[index + 1])  # Use proportion
                            value -= int(self.proportions[index + 1])  # Subtract proportion from value
                        
                        if instance_type in self.types[index]:
                            self.types[index][instance_type].append(number)  # Add number to existing list
                        else:
                            self.types[index][instance_type] = [number]  # Create new list of numbers
                    if instance_type in self.types[0]:
                        self.types[0][instance_type].append(value)  # Add remaining value to existing list
                    else:
                        self.types[0][instance_type] = [value]  # Create new list of remaining values
        return self.types

    def write_allocation(self, output_path, timestamp):
        # Method to write the allocation to a file
        lines = [['timestamp', 'market']]  # File header
        for instance_type in self.types[0]:
            lines[0].append(instance_type)  # Add instance types to header

        for index, hour in enumerate(timestamp['timestamp']):
            # Add lines for each allocation type and timestamp
            lines.extend([[hour, "on_demand"],
                          [hour, "sp_noupfront"],
                          [hour, "sp_partialupfront"],
                          [hour, "sp_allupfront"]])

            for instance_type in self.types[0]:
                lines[index * 4 + 1].append(str(self.types[0][instance_type][index]))  # Add on-demand data
                lines[index * 4 + 2].append(str(self.types[1][instance_type][index]))  # Add no upfront data
                lines[index * 4 + 3].append(str(self.types[2][instance_type][index]))  # Add partial upfront data
                lines[index * 4 + 4].append(str(self.types[3][instance_type][index]))  # Add all upfront data

        self.datam.write_file(lines, output_path)  # Write the allocation file using DataManagement
