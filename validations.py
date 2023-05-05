"""Performs input validations.

Validates on_demand_config.csv, reserves_config.csv, savings_plan_config.csv and total_demand.csv.
Those files are imported by build_simulation.py, which calls the functions on this module.
"""

def validate_on_demand_config(on_demand_config):
    validate_columns('on_demand_config', on_demand_config, ['instance', 'hourly_price'])
    validate_on_demand_instances(on_demand_config)

def validate_columns(file_name, data_frame, names):
    if list(data_frame.columns) != names:
        raise ValueError('The column names in ' + file_name +  ' are incorrect.')

def validate_on_demand_instances(on_demand_config):
    #Checks if the instances are unique
    instances = on_demand_config['instance'].values.tolist()
    instances.sort()
    unique_instances = list(on_demand_config['instance'].value_counts().index)
    unique_instances.sort()

    if (instances != unique_instances):
        raise ValueError('The instances names in on_demand_config should be unique')

def validate_reserves_config(reserves_config, instances):
    validate_columns('reserves_config', reserves_config, ['instance', 'market_name', 'hourly_price', 'upfront_price', 'duration'])
    validate_instances_names('reserves_config', reserves_config, instances)
    validate_reserves_markets(reserves_config, instances)

def validate_instances_names(file_name, data_frame, instances):
    #Checks if the instance names in the data_frame are the same as in the other files
    file_instances = list(data_frame['instance'].value_counts().index)
    file_instances.sort()

    if instances != file_instances:
        raise ValueError('The instances names in on_demand_config and ' + file_name + ' are not the same.')

def validate_reserves_markets(reserves_config, instances):
    #All instances should have the same reserve markets
    instance_line = reserves_config[reserves_config['instance'] == instances[0]]
    markets = list(instance_line.loc[:,'market_name'])
    markets.sort()
    previous_markets = markets
    
    for instance in instances:
        instance_line = reserves_config[reserves_config['instance'] == instance]
        markets = list(instance_line.loc[:,'market_name'])
        markets.sort()
        if markets != previous_markets:
            raise ValueError('Not all instances have the same reserve market names.')
        previous_markets = markets

def validate_savings_plan_config(savings_plan_config, instances):
    validate_columns('savings_plan_config', savings_plan_config, ['instance', 'hourly_price', 'duration'])
    validate_instances_names('savings_plan_config', savings_plan_config, instances)
    validate_savings_plan_durations(savings_plan_config)

def validate_savings_plan_durations(savings_plan_config):
    #All savings plan durations should be the same
    savings_plan_durations = list(savings_plan_config['duration'].value_counts().index)
    if len(savings_plan_durations) != 1:
        raise ValueError('All instances must have the same savings plan duration.')

def validate_demand(raw_demand, instances):
    if raw_demand.columns[0] != 'hour': #could i just correct in the code?
        raise ValueError('The first column name in the demand file is incorrect.')
    
    validate_demand_instances(raw_demand, instances)

def validate_demand_instances(raw_demand, instances):
    #the demand should contain all the instances passed on the input
    demand_col = list(raw_demand.columns)
    for instance in instances:
        if instance not in demand_col:
            raise ValueError('The instance ' + instance + ' is not on the demand file.')