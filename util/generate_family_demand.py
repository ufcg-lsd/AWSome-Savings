# This code generates tables with the demand of each instance family, using the TOTAL_demand file.

import pandas as pd

total_demand = pd.read_csv('TOTAL_demand.csv')

families = []
for i in range(1, len(total_demand.columns)):
    col = total_demand.columns[i]
    f = col[0]
    if (f not in families): families.append(f)

for f in families:
    output = pd.DataFrame(total_demand['Hour'].values.tolist(), columns=['Hour'])
    for col in total_demand.columns:
        if col[0] == f:
            value = total_demand[col].values.tolist()
            output[col] = value
    
    output.to_csv(f + '_demand.csv', index=False)