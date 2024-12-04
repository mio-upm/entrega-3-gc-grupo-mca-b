"""
Created on Tue Dec  3 13:06:41 2024
"""

import pandas as pd
import pulp as lp
from datetime import datetime, timedelta

df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)

#%%
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
    y = lp.LpVariable.dicts("y",[f for f in range(num_operaciones)], lowBound=0, cat="Integer") #todavia relajado
     
    #funcion objectivo
    problema += lp.lpSum(y[f]* precio_sombra[codigos[f]] for f in num_operaciones)   
    
    #restricciones
    problema += lp.lpSum(operaciones[i] * y[i] for i in num_operaciones ) <= W   # factibles
    
        
    for cod, confl in incompatibles.items(): #para cada operacion en el dic de incompatibles
        operacion_a = codigos.index[cod] #saco posicion f
        for operacion_b in range(len(confl)): 
            problema += y[operacion_a] + y[operacion_b] <= W
        
    problema.solve()
    
    f_objectivo = problema.objective()
    lista_solver = []   #lista de tuplas de operaciones con varValue > 0
    for v in problema.variables():
        if v.varValue >0:
            codigo_op = codigos.index(int(v.name.strip("y_")))
            fecha_inicio = operaciones.at(codigo_op)["Hora inicio "]
            fecha_fin = operaciones.at(codigo_op)["Hora fin"]
            lista_solver.append((codigo_op, fecha_inicio, fecha_fin))
            #print("Var: ",v.name," Valor: ",v.varValue )
    
    
    
    return f_objectivo, lista_solver



