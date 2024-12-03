"""
Created on Tue Dec  3 13:06:41 2024
"""

import pulp as lp
import numpy as np

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



# Definición del problema: 
problema = lp.LpProblem("Min_numero_quirofanos", lp.LpMinimize)

# Definición de variables:
y = []  # Variables que indican si un quirófano está siendo utilizado
x = []  # Variables que indican si una operación se asigna a un quirófano específico
# Inicialmente no conocemos cuántas columnas (planificaciones de quirófano) necesitaremos
# Por lo tanto, comenzaremos con una solución inicial factible (una planificación para cada operación)


""" PROBLEMA: NO VAMOS A IR UNO POR UNO DEFINIENDO LOS CONFLICTOS ENTRE LAS OPERACIONES

# Definir operaciones y conflictos
num_operaciones = 5
operaciones = [i for i in range(num_operaciones)]
conflictos = [
    [1],        # Operación 0 en conflicto con operación 1
    [0, 2],     # Operación 1 en conflicto con operaciones 0 y 2
    [1],        # Operación 2 en conflicto con operación 1
    [],         # Operación 3 sin conflictos
    [3]         # Operación 4 en conflicto con operación 3
]

"""

# Función objetivo:
problema += lp.lpSum(y)     

# Restricciones
    # Restricción: cada operación debe ser asignada a al menos un quirófano
    for i in range(num_operaciones):
        problema += lp.lpSum(x[i][k] for k in range(len(y))) == 1
    
    # Restricción: si una operación está en un quirófano, ese quirófano está siendo utilizado
    for i in range(num_operaciones):
        for k in range(len(y)):
            problema += x[i][k] <= y[k]
    
    # Restricción: operaciones conflictivas no pueden estar en el mismo quirófano
    for i in range(num_operaciones):
        for j in conflictos[i]:
            for k in range(len(y)):
                problema += x[i][k] + x[j][k] <= 1


# Generar la primera columna para iniciar con una solución factible
generar_columna(problema, operaciones, conflictos, y, x)


problema.solve()
print("Estado de la solución: ")
lp.LpStatus[problema.Status]

# Resultados
num_quirofanos_utilizados = sum([lp.value(y[k]) for k in range(len(y))])
print("Número mínimo de quirófanos necesarios: " num_quirofanos_utilizados)

for i in range(len(x)):
    for k in range(len(x[i])):
        if lp.value(x[i][k]) == 1:
            print(f"Operación {i} asignada al quirófano {k}")

# Continuar generando columnas hasta encontrar la solución óptima
while True:
    generar_columna(problema, operaciones, conflictos, y, x)
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
