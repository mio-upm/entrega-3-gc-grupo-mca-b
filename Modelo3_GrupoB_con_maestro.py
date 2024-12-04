# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 13:34:26 2024

@author: marta
"""


import pulp as lp
import numpy as np
import pandas as pd


df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)




#MAESTRO

#INDICES

# q : Quirófanos (p)
quirofanos = df_costes.index

# op: Operaciones (finales)
operaciones= df_operaciones.index

#PARÁMETROS

#demanda final de operaciones = 1, queremos que la operación esté asignada por lo menos 1 vez


#hay que crear unas planificaciones
    # a(q,op) nos dice si la operación op se hace en el quirofano q (1 si se hace 0 si no se hace) = B_ik

def planificación_inicial(operaciones, quirofanos):  #dataframes con operac ordenadas
    #objectivo es generar un conjunto de planificacion K
    K = { q: [] for q in quirofanos } #vamos a poner las operaciones de cada uno
    activados = []  #quirofanos activados
    num_activados = 0
    for codigo,op in operaciones.iterrows():
        t_inicio = op["Hora inicio "]
        t_fin = op["Hora fin"]
        # asigna operacion al primero quirofano disponible
        asignado = False

        i=0
        while i < len(activados) and not asignado:
            quiro = activados[i]
            if K[quiro][-1][2] <= t_inicio:
               #libre
               asignado = True
               K[quiro].append( (codigo, t_inicio, t_fin) )
            else: i+=1
        
        if not asignado: #nuevo
            asignado = True
            quiro = quirofanos[num_activados]
            K[quiro] = [ (codigo, t_inicio, t_fin) ]
            activados.append(quiro)
            num_activados+=1
    return K

def B_ik(operaciones, planificaciones):
    B_ik = {}
    for i in operaciones.index:
        for k in planificaciones.keys():
            long=len(planificaciones[k])
            lista_operaciones= [planificaciones[k][j][0] for j in range (long)]
            if i in lista_operaciones:
                B_ik[(i,k)] = 1 
            else: 
                B_ik[(i,k)] = 0
    return B_ik



def maestro(operaciones, planificaciones):
    #Definir problema
    problema = lp.LpProblem("Entrega 3 Modelo 3", lp.LpMinimize)
        
    #Definir variables 
    y = lp.LpVariable.dicts("y", [k for k in planificaciones.keys()], cat = lp.LpBinary)

    #Funcion objetivo 
    problema += lp.lpSum(C_k[(k)]*y[(k)] for k in planificaciones.keys())

    #Restriccion 1
    for i in equipos_medicos.index:
        problema += lp.lpSum(B_ik[(i, k)] * y[k] for k in planificaciones.keys()) >= 1

    problema.solve()
#VARIABLES

#RESTRICCIONES

#FUNCIÓN

#SOLUCIÓN QUE NOS DA tenemos que sacar de aquí los precios sombra


#GENERACIÓN DE COLUMNAS

#INDICES
# y(op): operaciones
