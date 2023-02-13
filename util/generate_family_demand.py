"""Generates tables with the demand of each instance family, using a demand file.

It receives the demand file path as an argument. 
This file should follow the same model as the TOTAL_demand.csv file in this folder.
The output is one csv file for each family, with the instances demand.
The output files have the same format as the input file.
"""

import sys
import pandas as pd

def main():
    validate_input()
    total_demand = get_total_demand()
    families = get_families_list(total_demand)

    for f in families:
        output = generate_family_demand(total_demand, f)
        output.to_csv(f + '_demand.csv', index=False)

def validate_input():
    if len(sys.argv) != 2:
        raise Exception("Number of input arguments incorrect. This script receives one argument, the demand file path.")

def get_total_demand():
    try:
        total_demand = pd.read_csv(sys.argv[1])
        return total_demand
    except:
        raise FileNotFoundError("File not found or path incorrect.")

#Each family is defined by the first letter of the instance name (c, m, t, ...)
def get_families_list(total_demand):
    families = []
    for i in range(1, len(total_demand.columns)):
        col = total_demand.columns[i]
        family = col[0]
        if (family not in families): families.append(family)
    return families

def generate_family_demand(total_demand, family):
    output = pd.DataFrame(total_demand['Hour'].values.tolist(), columns=['Hour'])
    for col in total_demand.columns:
        if col[0] == family:
            value = total_demand[col].values.tolist()
            output[col] = value
    return output

if __name__ == "__main__":
    main()