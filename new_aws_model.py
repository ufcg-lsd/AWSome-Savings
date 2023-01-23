from ortools.linear_solver import pywraplp
import copy

#Model for optimizing instance selection in aws ec2

# instance_values = [[[p_hr, p_up, y], [p_hr, p_up, y]], i = 0 
#                    [[p_hr, p_up, y], [p_hr, p_up, y]]] i = 1
# the first market in every instance is the savings plan market.
#
# demand = [[1, 2, ...], i=0
#           [1, 2, ...], i=1
#           [1, 2, ...]] i=2

#All instances have the same markets

# Equations format:
# List of times (T) -> List of instances (I) -> List of markets (M)
# 1° element of each T: [[s_t, rs_t]]
# 1° element of each I: [a_t,i,sp]

# [[[s_t, rs_t]], 
# [[a_t,i,sp], [a_t,i,m, r_t,i,m], [a_t,i,m, r_t,i,m]], i=0
# [[a_t,i,sp], [a_t,i,m, r_t,i,m], [a_t,i,m, r_t,i,m]]], i=1
# [... t=1

# input_sp = [p_sp_i0, p_sp_i1, p_sp_i2, ...]

def optimize_model(t, demand, input_data, input_sp, y_sp):

    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return
    
    infinity = solver.infinity()
   
    num_markets = len(input_data[0])
    num_instances = len(input_data)
    num_vars = ((2 * num_markets + 1) * num_instances + 2) * t

    x = {}
    for j in range(num_vars):
        x[j] = solver.IntVar(0, infinity, 'x[%i]' % j)
    print('Number of variables =', solver.NumVariables())

    #Adding constraints
    coefficientsBase = create_coefficients_base(t, num_instances, num_markets)

    #Demand <= 1*a
    constraint1(solver, x, num_vars, demand, coefficientsBase)
    # a_t = sum(r_t)
    constraint2(solver, x, num_vars, coefficientsBase, input_data)
    constraint3(solver, x, num_vars, coefficientsBase, input_sp)
    constraint4(solver, x, num_vars, coefficientsBase, y_sp)

    obj_func = [0, 1 * y_sp] #savings plan coefficients (0 * s_t + 1 * rs_t * y_sp) - considers in the begining the total reserve cost

    for instance in input_data:
        obj_func.append(0) #coefficient of number of active instances in savings plan (a_t,i,SP)
        for market in instance: #market = [p_hr, p_up, y]
            cr_im = market[0] * market[2] + market[1]
            obj_func.append(0) #a_im * 0
            obj_func.append(cr_im) #r_im * cr_im

    obj_func = obj_func * t

    objective = solver.Objective()
    for j in range(num_vars):
        objective.SetCoefficient(x[j], float(obj_func[j]))
    objective.SetMinimization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        values = []

        print('Objective value =', solver.Objective().Value())
        for j in range(num_vars):
            print(x[j].name(), ' = ', x[j].solution_value())
            values.append(x[j].solution_value())
        print()
        print('Problem solved in %f milliseconds' % solver.wall_time())
        print('Problem solved in %d iterations' % solver.iterations())
        print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

        return [solver.Objective().Value(), values]
    else:
        print('The problem does not have an optimal solution.')

def constraint1(solver, x, num_vars, demand, coefficientsBase):
    for i_time in range(len(coefficientsBase)):
        time = coefficientsBase[i_time]
        for i_instance in range(1, len(time)): #jumps savings plan coefficients
            coefficients = copy.deepcopy(coefficientsBase) #making a copy before altering the coefficients
            
            coefficients[i_time][i_instance][0] = [1] # 1 * a_t,i,SP
            for i_market in range(1, len(coefficients[i_time][i_instance])): #jumps savings plan market
                coefficients[i_time][i_instance][i_market] = [1,0]

            constraint_expr = change_coefficients_format(generate_array(coefficients), x, num_vars)
            solver.Add(sum(constraint_expr) >= demand[i_instance - 1][i_time])

def constraint2(solver, x, num_vars, coefficientsBase, input_data):
    for i_time in range(len(coefficientsBase)):
        time = coefficientsBase[i_time]
        for i_instance in range(1, len(time)): #jumps savings plan coefficients
            instance = time[i_instance]
            for i_market in range(1, len(instance)): #jumps savings plan market
                coefficients = copy.deepcopy(coefficientsBase) #making a copy before altering the coefficients

                coefficients[i_time][i_instance][i_market] = [1, -1]
                
                y = input_data[i_instance - 1][i_market - 1][2]
                reserve_duration = y - 1

                for i in range(i_time - 1, -1, -1):
                    if reserve_duration > 0:
                        coefficients[i][i_instance][i_market] = [0, -1]
                        reserve_duration -= 1
                    else: break

                constraint_expr = change_coefficients_format(generate_array(coefficients), x, num_vars)
                solver.Add(sum(constraint_expr) == 0)

def constraint3(solver, x, num_vars,coefficientsBase, input_sp):
    for i_time in range(len(coefficientsBase)):
        coefficients = copy.deepcopy(coefficientsBase) #making a copy before altering the coefficients

        coefficients[i_time][0][0] = [-1, 0] #total sp active value in t

        for i_instance in range(1, len(coefficients[i_time])): #pula os coef do SP
            coefficients[i_time][i_instance][0][0] = float([input_sp[i_instance - 1]][0])
        
        constraint_expr = change_coefficients_format(generate_array(coefficients), x, num_vars)
        solver.Add(sum(constraint_expr) <= 0)


def constraint4(solver, x, num_vars, coefficientsBase, y_sp):
    for i_time in range(len(coefficientsBase)):
        coefficients = copy.deepcopy(coefficientsBase) #making a copy before altering the coefficients

        coefficients[i_time][0][0] = [1, -1]

        reserve_duration = y_sp - 1
        for i in range(i_time - 1, -1, -1):
            if reserve_duration > 0:
                coefficients[i][0][0] = [0, -1]
                reserve_duration -= 1
            else: break

        constraint_expr = change_coefficients_format(generate_array(coefficients), x, num_vars)
        solver.Add(sum(constraint_expr) == 0)


def create_coefficients_base(t, num_instances, num_markets): #[[[[0,0], [0,0]], [[0,0], [0,0]]], [[[0,0], [0,0]], [[0,0], [0,0]]]] para t=2, i=2 e m=2
    coefficients = []
    for i_time in range(t):
        time_coef = [[[0, 0]]] #savings plan coefficients (0 * s_t + 1 * rs_t)
        for i_instance in range(num_instances):
            instance_coef = [[0]] #coefficient of number of active instances in savings plan (a_t,i,SP)
            for i_market in range(num_markets):
                market_coef = [0, 0]
                instance_coef.append(market_coef)
            time_coef.append(instance_coef)
        coefficients.append(time_coef)
    
    return coefficients

def change_coefficients_format(coefficientes, x, num_vars):
    constraint_expr = \
        [coefficientes[j] * x[j] for j in range(num_vars)]
    return constraint_expr

def generate_array(list):
    array = []
    for time in list:
        for instance in time:
            for market in instance:
                for value in market:
                    array.append(value)
    return array