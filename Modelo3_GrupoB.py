"""
Created on Tue Dec  3 13:06:41 2024
"""

import pandas as pd
import pulp as lp
from datetime import datetime, timedelta

df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)

#%% NUEVA PLANIFICACIÓN

#variante de modelo 2, con dos parametros más: lista de quirofanos en input + el ultimo q ha salido de la generacion de columnas
def nueva_planificacion(operaciones, costes, quirofanos_input, ultimo="Quirófano 1"):  #dataframes con operac ordenadas
    # version de nueva_p donde ya tenemos los quirofanos selecionados (la funcion dual nos devuelve una lista de quirof utilizados) 
    #objectivo es generar un conjunto de planificacion K factible
    
    #hay q comenzar desde el quirofano nuevo tb?
    val_inicio = quirofanos_input.index(ultimo)  #pasado como input
    quirofanos = quirofanos_input[val_inicio,:]+ quirofanos_input[:,val_inicio]
    
    
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



#%% GENERACIÓN DE COLUMNAS

#hay q sacar precios sombra de funcion primal

def generacion_columnas(precio_sombra,      )












'''
import pulp as lp
import numpy as np
import pandas as pd

def generar_columna(problema, operaciones, conflictos, y, x):
    
    # Generar una nueva columna (planificación de quirófano) utilizando el método de pricing
    nueva_y = lp.LpVariable("y", cat="Binary")
    y.append(nueva_y)
    nueva_x = [lp.LpVariable("x", cat="Binary") for i in range(len(operaciones))]
    for i in range(len(operaciones)):
        if len(x) <= i:
            x.append([])
        x[i].append(nueva_x[i])

    # Actualizar la función objetivo
    problema += lp.lpSum(y), "Minimizar el Número de Quirófanos Utilizados"

    # Actualizar restricciones
    # Restricción: cada operación debe ser asignada a al menos un quirófano
    for i in range(len(operaciones)):
        problema += lp.lpSum(x[i][k] for k in range(len(y))) == 1

    # Restricción: si una operación está en un quirófano, ese quirófano está siendo utilizado
    for i in range(len(operaciones)):
        for k in range(len(y)):
            problema += x[i][k] <= y[k]

    # Restricción: operaciones conflictivas no pueden estar en el mismo quirófano
    for i in range(len(operaciones)):
        for j in conflictos[i]:
            for k in range(len(y)):
                problema += x[i][k] + x[j][k] <= 1

# DESDE AQUI VA BENE ---------------------------

# PARÁMETROS:

archivo = "241204_datos_operaciones_programadas.xlsx"  
df = pd.read_excel(archivo)    

num_operaciones = len(df)
operaciones = [i for i in range(num_operaciones)]

# Crear la matriz de conflictos
matriz_conflictos = [[0] * num_operaciones for _ in range(num_operaciones)]

# Obtener las horas de inicio y fin
for i in range(num_operaciones):
    inicio_i = df.loc[i, 'Hora inicio ']    
    fin_i = df.loc[i, 'Hora fin']
    
    for j in range(i + 1, num_operaciones):  # Solo comparar operaciones posteriores para evitar duplicados
        inicio_j = df.loc[j, 'Hora inicio ']
        fin_j = df.loc[j, 'Hora fin']
        
        # Comprobar si las operaciones se solapan
        if (inicio_i < fin_j) and (inicio_j < fin_i):  # Si se solapan, hay conflicto
            matriz_conflictos[i][j] = 1
            matriz_conflictos[j][i] = 1  # El conflicto es bidireccional

print("Matriz de Conflictos:")
for fila in matriz_conflictos:
    print(fila)
    
# HASTA AQUI VA BENE ---------------------------



# PROBLEMA: 
problema = lp.LpProblem("Min_numero_quirofanos", lp.LpMinimize)

# VARIABLES:
y = []  # Variables que indican si un quirófano está siendo utilizado
x = []  # Variables que indican si una operación se asigna a un quirófano específico
# Inicialmente no conocemos cuántas columnas (planificaciones de quirófano) necesitaremos
# Por lo tanto, comenzaremos con una solución inicial factible (una planificación para cada operación)



# FOBJ:
problema += lp.lpSum(y)     

# RESTRICCIONES
# Restricción: cada operación debe ser asignada a al menos un quirófano
for i in range(num_operaciones):
    problema += lp.lpSum(x[i][k] for k in range(len(y))) == 1

# Restricción: si una operación está en un quirófano, ese quirófano está siendo utilizado
for i in range(num_operaciones):
    for k in range(len(y)):
        problema += x[i][k] <= y[k]

# Restricción: operaciones conflictivas no pueden estar en el mismo quirófano
for i in range(num_operaciones):
    for j in matriz_conflictos[i]:
        for k in range(len(y)):
            problema += x[i][k] + x[j][k] <= 1



# Generar la primera columna para iniciar con una solución factible
generar_columna(problema, operaciones, matriz_conflictos, y, x)



problema.solve()
print("Estado de la solución: ", lp.LpStatus[problema.status])


# RESULTADOS
num_quirofanos_utilizados = sum([lp.value(y[k]) for k in range(len(y))])
print("Número mínimo de quirófanos necesarios: ", num_quirofanos_utilizados)

for i in range(len(x)):
    for k in range(len(x[i])):
        if lp.value(x[i][k]) == 1:
            print(f"Operación {i} asignada al quirófano {k}")

# Continuar generando columnas hasta encontrar la solución óptima
while True:
    generar_columna(problema, operaciones, matriz_conflictos, y, x)
    problema.solve()
    print(f"Estado de la solución: {problema.status}")
    if problema.status != 1:  # Si el estado no es óptimo, detener el algoritmo
        break

# Mostrar resultados finales
num_quirofanos_utilizados = sum([lp.value(y[k]) for k in range(len(y))])
print(f"Número mínimo de quirófanos necesarios: {num_quirofanos_utilizados}")
for i in range(len(x)):
    for k in range(len(x[i])):
        if lp.value(x[i][k]) == 1:
            print(f"Operación {i} asignada al quirófano {k}")
'''