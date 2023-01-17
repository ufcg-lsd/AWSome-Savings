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

#Todas as instâncias com o mesmo número de mercados (e mercados iguais)

# Formato das equações:
# Lista de T -> Lista de I -> Lista de M
# 1° elemento de cada T: [[s_t, rs_t]]
# 1° elemento de cada I: [a_t,i,sp]

# [[[s_t, rs_t]], 
# [[a_t,i,sp], [a_t,i,m, r_t,i,m], [a_t,i,m, r_t,i,m]], i=0
# [[a_t,i,sp], [a_t,i,m, r_t,i,m], [a_t,i,m, r_t,i,m]]], i=1
# [... t=1

# input_sp = [p_sp_i0, p_sp_i1, p_sp_i2, ...]

def otimizaModelo(t, demand, input_data, input_SP, y_sp):

    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return

    #data = create_data_model()
    
    infinity = solver.infinity()

   
    num_markets = len(input_data[0])
    num_instances = len(input_data)
    num_vars = ((2 * num_markets + 1) * num_instances + 2) * t

    x = {}
    for j in range(num_vars):
        x[j] = solver.IntVar(0, infinity, 'x[%i]' % j)
    print('Number of variables =', solver.NumVariables())

    #Adding constraints
    coefficientsBase = criarListaBaseCoefficients(t, num_instances, num_markets)

    #Demand <= 1*a
    constraint1(solver, x, num_vars, demand, coefficientsBase)
    # a_t = sum(r_t)
    constraint2(solver, x, num_vars, coefficientsBase, input_data)
    constraint3(solver, x, num_vars, coefficientsBase, input_SP)
    constraint4(solver, x, num_vars, coefficientsBase, y_sp)

    obj_func = [0, 1 * y_sp] #coeficientes do savings plan (0 * s_t + 1 * rs_t * y_sp) - considera o custo total da reserva no início

    for instancia in input_data:
        obj_func.append(0) #coefficiente de num_instancias ativas em savings plans (a_t,i,sp)
        for mercado in instancia: #mercado = [p_hr, p_up, y]
            cr_im = mercado[0] * mercado[2] + mercado[1]
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
    for i_tempo in range(len(coefficientsBase)):
        tempo = coefficientsBase[i_tempo]
        for i_instancia in range(1, len(tempo)): #pula os coef do SP
            coefficients = copy.deepcopy(coefficientsBase) #fazendo uma cópia antes de alterar os coeficientes
            
            coefficients[i_tempo][i_instancia][0] = [1] # 1 * a_t,i,SP
            for i_mercado in range(1, len(coefficients[i_tempo][i_instancia])): #pula o merc SP
                coefficients[i_tempo][i_instancia][i_mercado] = [1,0]

            constraint_expr = converteCoeficientes(transformaEmArray(coefficients), x, num_vars)
            solver.Add(sum(constraint_expr) >= demand[i_instancia - 1][i_tempo])

def constraint2(solver, x, num_vars, coefficientsBase, input_data):
    for i_tempo in range(len(coefficientsBase)):
        tempo = coefficientsBase[i_tempo]
        for i_instancia in range(1, len(tempo)): #pula os coef do SP
            instancia = tempo[i_instancia]
            for i_mercado in range(1, len(instancia)): #pula o merc SP
                coefficients = copy.deepcopy(coefficientsBase) #fazendo uma cópia antes de alterar os coeficientes

                coefficients[i_tempo][i_instancia][i_mercado] = [1, -1]
                
                y = input_data[i_instancia - 1][i_mercado - 1][2]
                duracao_re = y - 1

                for i in range(i_tempo - 1, -1, -1):
                    if duracao_re > 0:
                        coefficients[i][i_instancia][i_mercado] = [0, -1]
                        duracao_re -= 1
                    else: break

                constraint_expr = converteCoeficientes(transformaEmArray(coefficients), x, num_vars)
                solver.Add(sum(constraint_expr) == 0)

def constraint3(solver, x, num_vars,coefficientsBase, input_SP):
    for i_tempo in range(len(coefficientsBase)):
        coefficients = copy.deepcopy(coefficientsBase)

        coefficients[i_tempo][0][0] = [-1, 0] #valor total ativo de sp em t

        for i_instancia in range(1, len(coefficients[i_tempo])): #pula os coef do SP
            coefficients[i_tempo][i_instancia][0][0] = float([input_SP[i_instancia - 1]][0])
        
        constraint_expr = converteCoeficientes(transformaEmArray(coefficients), x, num_vars)
        solver.Add(sum(constraint_expr) <= 0)


def constraint4(solver, x, num_vars, coefficientsBase, y_sp):
    for i_tempo in range(len(coefficientsBase)):
        coefficients = copy.deepcopy(coefficientsBase) #fazendo uma cópia antes de alterar os coeficientes

        coefficients[i_tempo][0][0] = [1, -1]

        duracao_re = y_sp - 1
        for i in range(i_tempo - 1, -1, -1):
            if duracao_re > 0:
                coefficients[i][0][0] = [0, -1]
                duracao_re -= 1
            else: break


        constraint_expr = converteCoeficientes(transformaEmArray(coefficients), x, num_vars)
        solver.Add(sum(constraint_expr) == 0)


def criarListaBaseCoefficients(t, num_instancias, num_mercados): #[[[[0,0], [0,0]], [[0,0], [0,0]]], [[[0,0], [0,0]], [[0,0], [0,0]]]] para t=2, i=2 e m=2
    coefficients = []
    for i_tempo in range(t):
        coef_tempo = [[[0, 0]]] #coeficientes do savings plan (0 * s_t + 1 * rs_t)
        for i_instancia in range(num_instancias):
            coef_instancia = [[0]] #coefficiente de num_instancias ativas em savings plans (a_t,i,SP)
            for i_mercado in range(num_mercados):
                coef_mercado = [0, 0]
                coef_instancia.append(coef_mercado)
            coef_tempo.append(coef_instancia)
        coefficients.append(coef_tempo)
    
    return coefficients

def converteCoeficientes(coefficientes, x, num_vars):
    constraint_expr = \
        [coefficientes[j] * x[j] for j in range(num_vars)]
    return constraint_expr

def transformaEmArray(lista):
    array = []
    for tempo in lista:
        for instancia in tempo:
            for mercado in instancia:
                for valor in mercado:
                    array.append(valor)
    return array