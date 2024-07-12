"""
Calculates the cost for the original market allocation of a demand, considering 
the current prices. Currently, supports the on-demand, all upfront reserve, partial
upfront reverve, no upfront reserve, all upfront savings plan, partial upfront savings
plan and no upfront savings plan markets.

Assumptions:
 - The cost of the reserves after the end time is not considered in the total cost
 - All markets have the same instance types
"""

def calculate(demand_on_demand, demand_all_up_reserved, demand_partial_up_reserved, demand_no_up_reserved, demand_all_up_savings_plan, demand_partial_up_savings_plan, demand_no_up_savings_plan, prices, reserve_duration):
    """ Calculates the hourly costs for an allocation.
    Args:
        demand_on_demand: a dict with instance types as keys and lists of the demand for the
            on-demand market as values.
        demand_all_up_reserved: a dict with instance types as keys and lists of the demand for the
            all upfront reserve market as values.
        demand_partial_up_reserved: a dict with instance types as keys and lists of the demand for the
            partial upfront reserve market as values.
        demand_no_up_reserved: a dict with instance types as keys and lists of the demand for the
            partial upfront reserve market as values.
        demand_all_up_savings_plan: a dict with instance types as keys and lists of the demand for the
            all upfront savings plan market as values.
        demand_partial_up_savings_plan: a dict with instance types as keys and lists of the demand for the
            partial upfront savings plan market as values.
        demand_no_up_savings_plan: a dict with instance types as keys and lists of the demand for the
            partial upfront savings plan market as values.
        prices: a dict with instance types as keys and objects with the market prices as values.
        reserve_duration: an integer that represents the reserve duration in hours for the reserves markets. All
            reserve markets must have the same reserve duration.
    Returns: a dictionary that contains, for each one of the 7 markets types, one dictionary with the families as keys
        and the list of hourly costs as values.
    """

    max_t = len(demand_on_demand[list(demand_on_demand.keys())[0]])

    # on-demand and reserves costs are grouped by instance type
    costs_od = get_on_demand_cost(demand_on_demand, prices)
    costs_all_up_re = get_all_up_reserved_cost(demand_all_up_reserved, prices, reserve_duration)
    costs_partial_up_re = get_partial_up_reserved_cost(demand_partial_up_reserved, prices, reserve_duration)
    costs_no_up_re = get_no_up_reserved_cost(demand_no_up_reserved, prices, reserve_duration)
    # savings plans costs are grouped by family
    costs_all_up_sp = get_all_up_savings_plan_cost(demand_all_up_savings_plan, prices, reserve_duration)
    costs_partial_up_sp = get_partial_up_savings_plan_cost(demand_partial_up_savings_plan, prices, reserve_duration)
    costs_no_up_sp = get_no_up_savings_plan_cost(demand_no_up_savings_plan, prices, reserve_duration)
    
    #grouping the on-demand and reserves costs by families
    costs_od = group_costs_by_family(costs_od, max_t)
    costs_all_up_re = group_costs_by_family(costs_all_up_re, max_t)
    costs_partial_up_re = group_costs_by_family(costs_partial_up_re, max_t)
    costs_no_up_re = group_costs_by_family(costs_no_up_re, max_t)

    output = {'OnDemand': costs_od, 'RAllUpfront': costs_all_up_re, 'RPartialUpfront': costs_partial_up_re,
              'RNoUpfront': costs_no_up_re, 'SpAllUpfront': costs_all_up_sp, 'SpPartialUpfront': costs_partial_up_sp,
              'SpNoUpfront': costs_no_up_sp}

    return output

def calculate_no_savings_plan(demand_on_demand, demand_all_up_reserved, demand_partial_up_reserved, demand_no_up_reserved, prices, reserve_duration):
    """ Calculates the hourly costs for an allocation without the savings plan market.
    """

    max_t = len(demand_on_demand[list(demand_on_demand.keys())[0]])

    # on-demand and reserves costs are grouped by instance type
    costs_od = get_on_demand_cost(demand_on_demand, prices)
    costs_all_up_re = get_all_up_reserved_cost(demand_all_up_reserved, prices, reserve_duration)
    costs_partial_up_re = get_partial_up_reserved_cost(demand_partial_up_reserved, prices, reserve_duration)
    costs_no_up_re = get_no_up_reserved_cost(demand_no_up_reserved, prices, reserve_duration)

    # grouping the on-demand and reserves costs by families
    # costs_od = group_costs_by_family(costs_od, max_t)
    # costs_all_up_re = group_costs_by_family(costs_all_up_re, max_t)
    # costs_partial_up_re = group_costs_by_family(costs_partial_up_re, max_t)
    # costs_no_up_re = group_costs_by_family(costs_no_up_re, max_t)
    
    output = {'OnDemand': costs_od, 'RAllUpfront': costs_all_up_re, 'RPartialUpfront': costs_partial_up_re,
              'RNoUpfront': costs_no_up_re}

    return output

def calculate_no_reserves(demand_on_demand, demand_all_up_savings_plan, demand_partial_up_savings_plan, demand_no_up_savings_plan, prices, reserve_duration):
    """ Calculates the hourly costs for an allocation without the reserves markets.
    """

    max_t = len(demand_on_demand[list(demand_on_demand.keys())[0]])

    # on-demand costs is grouped by instance type
    costs_od = get_on_demand_cost(demand_on_demand, prices)

    # savings plans costs are grouped by family
    costs_all_up_sp = get_all_up_savings_plan_cost(demand_all_up_savings_plan, prices, reserve_duration)
    costs_partial_up_sp = get_partial_up_savings_plan_cost(demand_partial_up_savings_plan, prices, reserve_duration)
    costs_no_up_sp = get_no_up_savings_plan_cost(demand_no_up_savings_plan, prices, reserve_duration)

    #grouping the on-demand costs by families
    costs_od = group_costs_by_family(costs_od, max_t)

    output = {'OnDemand': costs_od, 'RAllUpfront': costs_all_up_sp, 'RPartialUpfront': costs_partial_up_sp,
              'RNoUpfront': costs_no_up_sp}

    return output
    
def get_on_demand_cost(demand, prices):
    costs = {}
    for instance_type in demand:
        costs[instance_type] = []
        instance_demand = demand[instance_type]
        price = prices[instance_type].on_demand

        for i in range(len(instance_demand)):
            costs[instance_type].append(instance_demand[i] * price)
    
    return costs

def get_all_up_reserved_cost(demand, prices, reserve_duration):
    costs = {}
    for instance_type in demand:
        instance_demand = demand[instance_type]
        upfront_price = prices[instance_type].up_all_upfront

        costs[instance_type] = [0.0 for _ in range(len(instance_demand))]
        active_reserves = [0.0 for _ in range(len(instance_demand))]
        for t in range(len(instance_demand)):
            d = instance_demand[t]
            if d > active_reserves[t]:
                num_res = d - active_reserves[t]
                costs[instance_type][t] += num_res * upfront_price

                for i in range(t, min((t + reserve_duration), len(instance_demand))):
                    active_reserves[i] += num_res
    return costs

def get_partial_up_reserved_cost(demand, prices, reserve_duration):
    costs = {}
    for instance_type in demand:
        instance_demand = demand[instance_type]
        upfront_price = prices[instance_type].up_partial_upfront
        hourly_price = prices[instance_type].hr_partial_upfront

        costs[instance_type] = [0.0 for _ in range(len(instance_demand))]
        active_reserves = [0.0 for _ in range(len(instance_demand))]
        for t in range(len(instance_demand)):
            d = instance_demand[t]
            if d > active_reserves[t]:
                num_res = d - active_reserves[t]
                costs[instance_type][t] += num_res * upfront_price

                # adiciona o custo por hora das reservas
                for i in range(t, min((t + reserve_duration), len(instance_demand))):
                    active_reserves[i] += num_res
                    costs[instance_type][i] += num_res * hourly_price
    return costs

def get_no_up_reserved_cost(demand, prices, reserve_duration):
    costs = {}
    for instance_type in demand:
        instance_demand = demand[instance_type]
        hourly_price = prices[instance_type].hr_no_upfront

        costs[instance_type] = [0.0 for _ in range(len(instance_demand))]
        active_reserves = [0.0 for _ in range(len(instance_demand))]
        for t in range(len(instance_demand)):
            d = instance_demand[t]
            if d > active_reserves[t]:
                num_res = d - active_reserves[t]

                # adiciona o custo por hora das reservas
                for i in range(t, min((t + reserve_duration), len(instance_demand))):
                    active_reserves[i] += num_res
                    costs[instance_type][i] += num_res * hourly_price
    return costs

def get_all_up_savings_plan_cost(demand, prices, reserve_duration):
    families = get_families(demand)
    costs = {}
    
    for family in families:
        max_t = len(demand[families[family][0]])
        active_savings_plan = [0.0 for _ in range(max_t)]
        costs[family] = [0.0 for _ in range(max_t)]

        for t in range(max_t):
            cost = 0.0

            # soma o gasto de todas as instancias da família
            for instance_type in families[family]:
                upfront = prices[instance_type].sp_up_all_upfront
                effective_hourly = upfront / reserve_duration
                cost += demand[instance_type][t] * effective_hourly
                        
            if cost > active_savings_plan[t]:
                diff = cost - active_savings_plan[t]

                costs[family][t] += (diff * reserve_duration)
                for i in range(t, min(t + reserve_duration, max_t)):
                    active_savings_plan[i] += diff
    return costs

def get_partial_up_savings_plan_cost(demand, prices, reserve_duration):
    families = get_families(demand)
    costs = {}
    
    for family in families:
        max_t = len(demand[families[family][0]])
        active_savings_plan = [0.0 for _ in range(max_t)]
        costs[family] = [0.0 for _ in range(max_t)]

        for t in range(max_t):
            cost = 0.0

            # soma o gasto de todas as instancias da família
            for instance_type in families[family]:
                upfront = prices[instance_type].sp_up_partial_upfront
                hourly = prices[instance_type].sp_hr_partial_upfront
                effective_hourly = hourly + upfront / reserve_duration
                cost += demand[instance_type][t] * effective_hourly
            
            if cost > active_savings_plan[t]:
                diff = cost - active_savings_plan[t]

                #considerando que, no partial upfront, 50% do total é pago upfront
                costs[family][t] += (diff * reserve_duration) / 2
                for i in range(t, min(t + reserve_duration, max_t)):
                    active_savings_plan[i] += diff
                    costs[family][i] += diff / 2
    return costs

def get_no_up_savings_plan_cost(demand, prices, reserve_duration):
    families = get_families(demand)
    costs = {}

    for family in families:
        max_t = len(demand[families[family][0]])
        active_savings_plan = [0.0 for _ in range(max_t)]
        costs[family] = [0.0 for _ in range(max_t)]

        for t in range(max_t):
            cost = 0.0

            # soma o gasto de todas as instancias da família
            for instance_type in families[family]:
                hourly = prices[instance_type].sp_hr_no_upfront
                effective_hourly = hourly
                cost += demand[instance_type][t] * effective_hourly
            
            if cost > active_savings_plan[t]:
                diff = cost - active_savings_plan[t]

                for i in range(t, min(t + reserve_duration, max_t)):
                    active_savings_plan[i] += diff
                    costs[family][i] += diff
    return costs

def group_costs_by_family(costs, max_t):
    families = get_families(costs)
    grouped_costs = {}
    for family in families:
        grouped_costs[family] = [0.0 for _ in range(max_t)]

    for instance_type in costs:
        if len(instance_type.split('.')) == 1:
            family = instance_type
        else: 
            family, type = instance_type.split('.')

        instance_costs = costs[instance_type]
        for t in range(len(instance_costs)):
            grouped_costs[family][t] += instance_costs[t]

    return grouped_costs

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

class InstancePrices:
    def __init__(self, on_demand, up_all_upfront, up_partial_upfront, hr_partial_upfront, hr_no_upfront, sp_up_all_upfront, sp_up_partial_upfront, sp_hr_partial_upfront, sp_hr_no_upfront):
        self.on_demand = on_demand
        self.up_all_upfront = up_all_upfront
        self.up_partial_upfront = up_partial_upfront
        self.hr_partial_upfront = hr_partial_upfront
        self.hr_no_upfront = hr_no_upfront
        self.sp_up_all_upfront = sp_up_all_upfront
        self.sp_up_partial_upfront = sp_up_partial_upfront
        self.sp_hr_partial_upfront = sp_hr_partial_upfront
        self.sp_hr_no_upfront = sp_hr_no_upfront