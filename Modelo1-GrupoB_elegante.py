# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 12:38:53 2024

"""
import pulp as lp
import pandas as pd
import datetime as dt

df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)

equipos_cardiologia_pediatrica = df_operaciones[df_operaciones["Especialidad quirúrgica"]=="Cardiología Pediátrica"]
equipos_medicos = equipos_cardiologia_pediatrica.loc[:,'Equipo de Cirugía']

quirofanos = df_costes.index.tolist()
#%%
n=0
# diccionario con nodo y lista de op non compatibles
L = { x:set() for x in equipos_cardiologia_pediatrica.index}

for codigo_a, a in equipos_cardiologia_pediatrica.iterrows():
    incompat = []    
    #guardar data de la op
    a_inicio = a['Hora inicio ']
    a_fin = a['Hora fin']
    n += 1

    for num in range(n, len(equipos_cardiologia_pediatrica)):        
        b = equipos_cardiologia_pediatrica.iloc[num,:]
        #comparar data inicio y fin
        b_inicio = b['Hora inicio ']
        b_fin = b['Hora fin']
        codigo_b = equipos_cardiologia_pediatrica.index[num]
        
        if a_inicio <= b_inicio: 
            if a_fin > b_inicio:  #incompatible
                L[codigo_a].add(codigo_b)
                L[codigo_b].add(codigo_a)
        else:
            if b_fin > a_inicio:
                L[codigo_a].add(codigo_b)
                L[codigo_b].add(codigo_a)

#%%
# Los costes se encuentran en la matriz de costes y se filtran al llamar al conjunto de cardiologia pediatrica
codigos_op = equipos_medicos.index

problema = lp.LpProblem("Entrega_Modelo_1", lp.LpMinimize)

#Definir las variables
x = lp.LpVariable.dicts("x", [(i,j) for i in codigos_op for j in quirofanos], cat = lp.LpBinary)

#Funcion objetivo
problema += lp.lpSum(df_costes.loc[j,i]*x[(i,j)] for i in codigos_op for j in quirofanos)

#Restriccion 1
for i in codigos_op:
    problema += lp.lpSum(x[(i,j)] for j in quirofanos) >= 1
    
#Restriccion 2
for i in codigos_op:
    for j in quirofanos: 
        problema += lp.lpSum(x[(h,j)] for h in codigos_op if h in L[i]  ) + x[(i,j)] <= 1

problema.solve(lp.PULP_CBC_CMD(msg=False))

valor_solucion=problema.objective.value()

print(f'El coste de la planificación es de {valor_solucion}')

count = 0
for v in problema.variables():
    if v.varValue >0:
        count += 1
        print('Se asigna la operación ',v.name.split('_')[1]+" "+v.name.split('_')[2]+" "+v.name.split('_')[3]+')',' al ',v.name.split('_')[4]+" "+v.name.split('_')[5])

        
print('Se abren ',count, ' quirófanos')

