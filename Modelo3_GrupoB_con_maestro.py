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
operaciones= df_operaciones

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

def Bik(operaciones, planificaciones):
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


def maestro_relajado(operaciones, planificaciones):
    #Definir problema
    problema = lp.LpProblem("Entrega 3 Modelo 3", lp.LpMinimize)
    B_ik=Bik(operaciones, planificaciones)  
    #Definir variables 
    x = lp.LpVariable.dicts("x", [k for k in planificaciones.keys()], lowBound=0, cat = lp.LpContinuous)

    #Funcion objetivo 
    problema += lp.lpSum(x[(k)] for k in planificaciones.keys())

    #Restriccion 1
    for i in operaciones.index:
        problema += lp.lpSum(B_ik[(i, k)] * x[k] for k in planificaciones.keys()) >= 1

    #resolución
    #ahora queremos sacar de esta función los precios sombra
    problema.solve(lp.PULP_CBC_CMD(msg=False))
   # print(problema.solve())
   # print([{name:c.pi} for name, c in problema.constraints.items()])
    return problema.objective.value(), {name:c.pi for name, c in problema.constraints.items()}


prueba= maestro_relajado(operaciones,planificación_inicial(operaciones, quirofanos))    


#MAESTRO SIN RELAJAR

def maestro(operaciones, planificaciones):
    #Definir problema
    problema = lp.LpProblem("Entrega 3 Modelo 3", lp.LpMinimize)
    B_ik=Bik(operaciones, planificaciones)  
    #Definir variables 
    x = lp.LpVariable.dicts("x", [k for k in planificaciones.keys()], lowBound=0, cat = lp.LpBinary)

    #Funcion objetivo 
    problema += lp.lpSum(x[(k)] for k in planificaciones.keys())

    #Restriccion 1
    for i in operaciones.index:
        problema += lp.lpSum(B_ik[(i, k)] * x[k] for k in planificaciones.keys()) >= len(operaciones)

    #resolución
    #ahora queremos sacar de esta función los precios sombra
    problema.solve(lp.PULP_CBC_CMD(msg=False))
   # print(problema.solve())
   # print([{name:c.pi} for name, c in problema.constraints.items()])
    variables={}
    for v in problema.variables():
        variables[v.name]=v.value()
    return problema.objective.value(), variables

#GENERACIÓN DE COLUMNAS


def conflictos(df_operaciones):
    # Crear el diccionario de incompatibilidades
    L = {x: set() for x in df_operaciones.index}

    # Iterar por las filas para calcular incompatibilidades
    n = 0
    for codigo_a, a in df_operaciones.iterrows():
        a_inicio = a['Hora inicio ']
        a_fin = a['Hora fin']
        n += 1
        for num in range(n, len(df_operaciones)):
            b = df_operaciones.iloc[num, :]
            b_inicio = b['Hora inicio ']
            b_fin = b['Hora fin']
            codigo_b = df_operaciones.index[num]

            # Comparar horarios para determinar incompatibilidad
            if a_inicio <= b_inicio:
                if a_fin > b_inicio:  # Incompatible
                    L[codigo_a].add(codigo_b)
                    L[codigo_b].add(codigo_a)
            else:
                if b_fin > a_inicio:  # Incompatible
                    L[codigo_a].add(codigo_b)
                    L[codigo_b].add(codigo_a)
    return L


def problema_dual(operaciones, precio_sombra):
    # buscamos generacion de combinacion de operaciones
    #precio_sombra = diccionario { operacion: precioS    }
    #operaciones = dataFrame de operaciones
    
    incompatibles = conflictos(operaciones) #diccionario con cada ope y su incompatibles
    num_operaciones = len(operaciones)  #finales
    codigos = operaciones.index.tolist() #los codigos de las operaciones
    W=1 #longitud
    
    problema = lp.LpProblem("Entrega 3 Modelo dual", lp.LpMaximize)
    y = lp.LpVariable.dicts("y",codigos, lowBound=0, cat="Integer") #todavia relajado
     
    #funcion objectivo
    problema += lp.lpSum(y[cod]* precio_sombra[cod] for cod in codigos)   
    
    #restricciones   

    for i in codigos:
        for j in incompatibles[i]:
            problema+= y[i]+y[j]<=W
        
        
    problema.solve(lp.PULP_CBC_CMD(msg=False))
    
    f_objectivo = problema.objective.value()
    lista_solver = []   #lista de tuplas de operaciones con varValue > 0
    for v in problema.variables():
        if v.varValue >0:
            codigo_op = v.name.strip("y_")
            fecha_inicio = operaciones.loc[codigo_op,"Hora inicio "]
            fecha_fin = operaciones.loc[codigo_op,"Hora fin"]
            lista_solver.append((codigo_op, fecha_inicio, fecha_fin))
            #print("Var: ",v.name," Valor: ",v.varValue )
    
    
    
    return f_objectivo, lista_solver



fobj_generacion= 100
#hay que generar una planificación de partida

planificaciones=planificación_inicial(operaciones, quirofanos)

#condición de parar fobj de generacion columnas <= 1 


while fobj_generacion>1:
    #resolver el maestro relajado con una planificacion
    
    #sacar el precio sombra

    sol_maestro, precio_sombra = maestro_relajado(operaciones, planificaciones)
    dict_precio_sombra={}
    
    i=0   
    for k, v in precio_sombra.items():
        dict_precio_sombra[operaciones.index[i]]=v
        i+=1

#crear nueva f obj para generación de columnas y actualizar fobj 

    fobj_generacion, nueva_planif= problema_dual(operaciones, dict_precio_sombra)

#poner planificaciones
    nuevo_quirofano=len(planificaciones)+1
    planificaciones[f'Quirofano {nuevo_quirofano}']=nueva_planif

#RESOLVEMOS MAESTRO SIN RELAJAR

num_quirofanos, variables = maestro(operaciones, planificaciones)


print(f'Usaremos {num_quirofanos}')

