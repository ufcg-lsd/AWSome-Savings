import click
import subprocess
import sys

from services.calculator import calculate_no_savings_plan, calculate_no_reserves
from services.optimizer_util import generate_optimizer_input
from services.data_management import DataManagement

# Hours in a year
DURATION = 8760

@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path(exists=False))
@click.option('--m', default='classic', 
              help='How the cost for demand will be calculated: [classic] - Default. Tries to maintain the aspect ratio specified in the configuration metadata. ' + '[optimal] - Calculates the optimal solution.')
@click.option('--p', 
              type=(str, float, float, float, float), 
              default=('proportion', 1, 0, 0, 0), 
              help='How instances will be purchased in the classic method. [Proportion] or [Absolute] followed by 4 values that define the sizes of OnDemand, NoUpfront, PartialUpfront and AllUpfront.')
@click.option('--prices_path', 
              default='/calculation/data/prices.csv', 
              help='File with prices to be considered at calculation.')
@click.option('--no_savings_plans',
              is_flag=True,
              default=False,
              help='Disables savings plans unit data processing')
@click.option('--configure_prices',
              is_flag=True,
              default=False,
              help='Makes the CLI fetch the instances prices again')
@click.option('--summarize',
              is_flag=True,
              default=False,
              help='Summarizes output data to prices by market (used only for classic or advisor)')
def main(input_path, output_path, prices_path, m, p, no_savings_plans, configure_prices, summarize):
    """
    Costplanner calculate by CLI.
    """
    method = m.lower()

    match method:
        case 'classic':
            if p == None:
                click.echo('You must use --p to define the instances that will be purchased for each market.')
                sys.exit(1)
            classic_calc(prices_path, input_path, output_path, no_savings_plans, summarize, p)
        case 'optimal':
            optimal_calc(prices_path, input_path, output_path)
        case _:
            click.echo("Invalid method. Try 'classic' or 'optimal'.")

        
def classic_calc(prices_path, input_path, output_path, no_savings_plans, summarize, proportions):
    split_path = output_path.split("/")
    exec_name = split_path[len(split_path) - 1]
    
    datam = DataManagement()
    # The proportion will be an string if this function be called by the bash
    if type(proportions) == str:
        no_savings_plans = bool(int(no_savings_plans))
        summarize = bool(int(summarize))
        proportions = proportions.strip('()').split(', ')
        proportions = (proportions[0], eval(proportions[1])/100.0, eval(proportions[2]), 1 - eval(proportions[3])/100.0, eval(proportions[4]))

    prices = datam.read_prices(prices_path)
    demand = datam.read_demand(input_path)
    ond_data, nop_data, pup_data, allup_data = datam.slice_classic_data(demand, proportions)
    if no_savings_plans:
        output = calculate_no_savings_plan(ond_data, allup_data, pup_data, nop_data, prices, DURATION)
    else:
        output = calculate_no_reserves(ond_data, allup_data, pup_data, nop_data, prices, DURATION)      

    '''
    If this function is beeing used for advisor calc
    We will need to calculate the prices for each instante(column) of this dataframe 
    '''

    if summarize:
        output = join_markets(output)
        datam.write_output_summarize(output, f"{output_path}/{exec_name}.csv")
    else:
        datam.write_output(output, f"{output_path}/{exec_name}.csv")
    

def optimal_calc(prices_path, input_path, output_path):
    split_path = output_path.split("/")
    exec_name = split_path[len(split_path) - 1]
    
    generate_optimizer_input(input_path, prices_path, exec_name)
        
    optimization_args = ['python3', 
                        f'/calculation/services/run_optimizations.py', 
                        exec_name,
                        f'{output_path}/{exec_name}.csv']
    
    with open('log.txt', "w") as file:
        proc = subprocess.Popen(optimization_args, stderr=file)
        proc.wait()


def join_markets(costs):
    """ Groups the hourly costs by markets
    Args:
        - costs: a dictionary that contains, for each one of the 7 market types, one dictionary 
        with the families as keys and the list of hourly costs as values.
    Returns: a dictionary with the market types as keys and the list of hourly costs as values
    """
    max_t = len(costs['OnDemand'][list(costs['OnDemand'].keys())[0]])
    grouped_costs = {}
    
    for market in costs:
        grouped_costs[market] = [0 for _ in range(max_t)]
        market_costs = costs[market]
        
        for family in market_costs:
            family_costs = market_costs[family]
            for t in range(len(family_costs)):
                grouped_costs[market][t] += family_costs[t]
        
    return grouped_costs


def get_total_cost(output):
    """ Given the output of the classic mode (not summarized), returns the total cost for the allocation.
    """
    total_cost = 0
    for market in output:
        costs = output[market]
        for family in costs:
            total_cost += sum(costs[family])
    
    return total_cost


if __name__ == '__main__':
    main()
