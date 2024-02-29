import os
import subprocess
import sys
import csv
import time

HOUR = 3600
TIME_WAITING_RESULTS = 30
EXEC_ID = sys.argv[1]
EXEC_OUTPUT = sys.argv[2]

def filter_optimization_output(path_to_filter):
    new_timestamp = []
    with open(f'{path_to_filter}', 'r') as demand_file:
        demand_reader = csv.reader(demand_file)
        # Ignore the first line(header)
        next(demand_reader, None)
        # The list comprehension below remove the 4th column (count_active)
        no_active_reserves = [row[:3] + row[4:] for row in demand_reader]
        # The list comprehension below put the timestamp in seconds
        new_timestamp = [[int(row[0]) * HOUR] + row[1:] for row in no_active_reserves]
        
    return new_timestamp


def write_output(execution_dir, exec_output=EXEC_OUTPUT):
    first_family = True
    with open(f"{execution_dir}/final_result.csv", 'w') as output_file:
        output_writer = csv.writer(output_file)
        # If the first family is writing the output, we need to put a header
        if first_family:
            first_family = False
            output_writer.writerow(['timestamp','flavor', 'market', 'number'])
        # Iterates over the families directory
        for family in os.listdir(f"{execution_dir}/raw"):
            demand_directory = os.listdir(f"{execution_dir}/raw/{family}/")
            # Iterates over the demand output of a family and filter the columns
            for demand_file in demand_directory:
                file_type = demand_file.split('.')[0]
                if file_type == f"total_purchases_{family}":
                    filter_optimization = filter_optimization_output(f"{execution_dir}/raw/{family}/{demand_file}")
                    output_writer.writerows(filter_optimization)
    os.popen(f'cp {execution_dir}/final_result.csv {exec_output}')
 
def run_optimizations(execution_dir):
    # Function to run optimization for a family
    for family in os.listdir(f'{execution_dir}/input'):
        os.makedirs(f'{execution_dir}/raw/{family}', exist_ok=True)
        optimization_args = [f'/calculation/optimizer/build/opt.elf', 
                        f'{execution_dir}/input/{family}/on_demand_config.csv',
                        f'{execution_dir}/input/{family}/savings_plan_config.csv',
                        f'{execution_dir}/input/{family}/demand.csv',
                        f'{execution_dir}/raw/{family}']
        
        optimization = subprocess.Popen(optimization_args)
        optimization.wait()

        while not os.path.isfile(f'{execution_dir}/raw/{family}/result_cost.csv'):
            time.sleep(TIME_WAITING_RESULTS)

    write_output(execution_dir)

if __name__ == "__main__":
    # Run the optimizations
    execution_dir = f"/tmp/costplanner_playpen/optimizer/{EXEC_ID}"
    run_optimizations(execution_dir)
    