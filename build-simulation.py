import csv
import pandas as pd
from new_aws_model import otimizaModelo

def checkInputSP(sp_input, instances): #Fazer
    #if sp_input['instance'].value_counts() != instances: return False
    #if len(sp_input['y'].value_counts()) != 1: return False

    return True

def outputInstances(values, t, instance_names, market_names, input_data, writerCost): #como calcular o custo por instancia se o custo do savings plan é compartilhado?

    for i_instancia in range(len(instance_names)):
        cost = 0

        output = open('total_purchases_' + instance_names[i_instancia] + '.csv', 'w')
        writer = csv.writer(output)
        writer.writerow(['instanceType', 'market', 'count_active', 'count_reserves'])

        #Savings plan
        for i_tempo in range(t):
            activ = values[i_tempo][i_instancia + 1][0][0]
            writer.writerow([instance_names[i_instancia], 'savings_plan', activ, 0])

            #por enquanto, o custo individual das instâncias não considera o custo do savings plan
                
        #Others
        for i_mercado in range(len(market_names)):
            im_values = input_data[i_instancia][i_mercado]
            cr_im = im_values[0] * im_values[2] + im_values[1]

            for i_tempo in range(t):
                activ = values[i_tempo][i_instancia + 1][i_mercado + 1][0]
                reserves = values[i_tempo][i_instancia + 1][i_mercado + 1][1]
                writer.writerow([instance_names[i_instancia], market_names[i_mercado], activ, reserves])

                cost += reserves * cr_im

        writerCost.writerow([instance_names[i_instancia], cost])        
        output.close()

def outputSavingsPlan(values, t, y_sp, writerCost):
    output = open('total_purchases_savings_plan.csv', 'w')
    writer = csv.writer(output)
    writer.writerow(['market', 'value_active', 'value_reserves'])
    cost = 0

    for i_tempo in range(t):
        values_sp = values[i_tempo][0][0]
        cost += values_sp[1] * y_sp
        writer.writerow(['savings_plan', values_sp[0], values_sp[1]])

    writerCost.writerow(['savings_plan', cost])


def tranformarEmLista(values, t, num_instances, num_markets):
    index = 0
    lista = []
    for i_tempo in range(t):
        lista_tempo = []
        lista_tempo.append([[values[index], values[index + 1]]])
        index += 2
        for i_instancia in range(num_instances):
            lista_instancia = []
            lista_instancia.append([values[index]])
            index += 1
            for i_mercado in range(num_markets):
                lista_instancia.append([values[index], values[index + 1]])
                index += 2
            lista_tempo.append(lista_instancia)
        lista.append(lista_tempo)
    return lista

raw_input = pd.read_csv('data/input.csv')
raw_sp_input = pd.read_csv('data/input_sp.csv')
instances = raw_input['instance'].value_counts()

if checkInputSP(raw_sp_input, instances) == False:
    raise ValueError("Error in the savings plan input.")

raw_demand = pd.read_csv('data/TOTAL_demand.csv')

resultCost = open('data/resultCost.csv', 'w')
writerCost = csv.writer(resultCost)
writerCost.writerow(['instance','total_cost'])

input_data = []
input_sp = []
total_demand = []
instance_names = []

for instance in instances.index:
    line_sp = raw_sp_input[raw_sp_input['instance'] == instance]
    input_sp.append(line_sp['p_hr'])
    instance_input = []
    market_names = []
    instance_names.append(instance)

    for i in range(len(raw_input)):
        line = raw_input.iloc[i]
        if line['instance'] == instance:
            instance_input.append([line['p_hr'],line['p_up'], line['y']])
            market_names.append(line['market_name'])
    input_data.append(instance_input)

    instance_demand = raw_demand[instance].values.tolist()
    total_demand.append(instance_demand)

t = len(total_demand[0])
y_sp = (raw_sp_input.iloc[0])['y']

result = otimizaModelo(t, total_demand, input_data, input_sp, y_sp)
cost = result[0]
values = tranformarEmLista(result[1], t, len(instance_names), len(market_names))

writerCost.writerow(['all', cost])

outputSavingsPlan(values, t, y_sp, writerCost)
outputInstances(values, t, instance_names, market_names, input_data, writerCost)