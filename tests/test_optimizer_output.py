import subprocess
import os
import csv
from pathlib import Path

ROOT_DIRECTORY = Path('.').resolve()

# Path to the demand file. You can change this to point to your test file.
DEMAND_PATH = f'{ROOT_DIRECTORY}/tests/mock_data/4_instances.csv'
PLAYPEN = f"/tmp/tests/playpen"

# Create the input and output directories in the playpen.
[os.makedirs(f"{PLAYPEN}/{path}", exist_ok=True) for path in ["input", "output"]]

def test_demand_output():
    """
    This test runs the allocation optimizer script with the given demand file and checks if the output allocation matches the demand.
    """

    optimization_args = ["python3",
                         f"{ROOT_DIRECTORY}/costplanner_cli.py",
                         DEMAND_PATH,
                         f"{PLAYPEN}/output/",
                         "--m",
                         "optimal"]

    # Run the optimizer script and redirect stderr to a log file.
    with open('/tmp/tests/log.txt', encoding="utf-8", mode="w") as file:
        proc = subprocess.Popen(optimization_args, stderr=file)
    proc.wait()

    # Read the allocation numbers from the output and demand files.
    allocation_optimizer = read_allocation_number(2, f"{PLAYPEN}/output/allocation.csv")
    demand = read_allocation_number(1, DEMAND_PATH)

    # Check if the allocation matches the demand, we are allowing an error of 1 instance by family.
    for key in demand:
        assert allocation_optimizer[key] - demand[key] <= 1
    
    os.system('rm -rf /tmp/tests')

def read_allocation_number(start_column, alloc_or_demand_path):
    """
    Reads allocation or demand numbers from a CSV file starting from a specified column.
    Returns a dictionary with headers as keys and the sum of corresponding column values as values.
    """
    data_sums = {}
    with open(alloc_or_demand_path, mode='r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)

        for row in csv_reader:
            for i in range(start_column, len(headers)):
                if headers[i] not in data_sums:
                    data_sums[headers[i]] = int(row[i])
                else:
                    data_sums[headers[i]] += int(row[i])
    return data_sums