# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 12:38:53 2024

"""
import pulp as lp
import pandas as pd

df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)

equipos_cardiologia_pediatrica = df_operaciones[df_operaciones["Especialidad quirúrgica"]=="Cardiología Pediátrica"]
equipos_medicos = equipos_cardiologia_pediatrica.loc[:,'Equipo de Cirugía']

quirofanos = df_costes.index

#C = {(i, j): [df_costes.loc[i, j] for i in equipos_cardiologia_pediatrica for j in str(df_costes.index)]}

# Los costes se encuentran en la matriz de costes y se filtran al llamar al conjunto de cardiologia pediatrica

problema = lp.LpProblem("Entrega 3 Modelo 1", lp.LpMinimize)

#Definir las variables
x = lp.LpVariable.dicts("x", [(i,j) for i in equipos_medicos for j in quirofanos], lowBound = 0, cat = lp.LpBinary)

#Funcion objetivo
problema += lp.lpSum(df_costes[(i,j)]*x[(i,j)] for i in equipos_medicos for j in quirofanos)

#Restriccion 1
for i in equipos_medicos:
    problema += lp.lpSum(x[(i,j)] for j in quirofanos) >= 1
    
#Restriccion 2
for i in equipos_medicos:
    for j in quirofanos: 
        problema += lp.lpSum(x[(h,j)] for h in L) + x[(i,j)] <= 1
