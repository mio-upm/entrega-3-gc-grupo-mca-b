# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 17:11:19 2024

@author: UX431
"""

import pulp as lp 
import numpy as np
import pandas as pd
import datetime as dt

df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)

operaciones = list(df_operaciones.index)
num_operaciones = len(df_operaciones)
quirofanos = list(df_costes.index)
num_quirofanos = len(quirofanos)

n=0
# diccionario con nodo y lista de op non compatibles
L = {x: set() for x in df_operaciones.index}

for codigo_a, a in df_operaciones.iterrows():
    # Guardar datos de la operación actual
    a_inicio = a['Hora inicio ']
    a_fin = a['Hora fin']
    n += 1

    # Comparar con operaciones posteriores
    for num in range(n, len(df_operaciones)):
        b = df_operaciones.iloc[num, :]
        b_inicio = b['Hora inicio ']
        b_fin = b['Hora fin']
        codigo_b = df_operaciones.index[num]

       # Detectar conflicto
        if a_inicio <= b_inicio:
            if a_fin > b_inicio:  # Solapamiento
                L[codigo_a].add(codigo_b)
                L[codigo_b].add(codigo_a)
        else:
            if b_fin > a_inicio:  # Solapamiento
                L[codigo_a].add(codigo_b)
                L[codigo_b].add(codigo_a)

                
#Definir variables 
x = lp.LpVariable.dicts('x', [(i,j) for i in range(1,num_operaciones) for j in range(1,num_quirofanos)], cat = lp.LpInteger)
y = lp.LpVariable.dicts('y', [j for j in range(1,num_quirofanos)], cat = lp.LpInteger)

# Crear el problema
problema = lp.LpProblem("Minimizar Quirófanos", lp.LpMinimize)
  
#Restriccion 1

for i in range(1, num_operaciones): 
    problema += lp.lpSum(x[(i,j)] for j in range(1,num_quirofanos)) == 1 
    
#Restriccion 2

for i in range(1, num_operaciones):
    for j in range(1,num_quirofanos):
        problema += x[(i,j)] <= y[j]
        
#Restriccion 3



for codigo, conflictos in L.items():
    operacion_a = operaciones.index(codigo)
    for operacion_b in range(len(conflictos)):
        for j in range(1,num_quirofanos):
            problema += x[(operacion_a, j)] + x[(operacion_b, j)] <= 1

    

