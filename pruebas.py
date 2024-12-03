#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 17:44:22 2024

"""

from pulp import LpProblem, LpMinimize, LpVariable, lpSum

# Conjuntos
operaciones = list(range(1, 5))  # Ejemplo: operaciones 1, 2, 3, 4
quirofanos = list(range(1, 10))  # Máximo posible de quirófanos

# Ejemplo de incompatibilidades (solapamiento)
incompatibles = [(1, 3), (2, 4)]  # Operaciones incompatibles

# Crear el modelo
model = LpProblem("Minimizar_Quirófanos", LpMinimize)

# Variables
x = LpVariable.dicts("x", [(i, j) for i in operaciones for j in quirofanos], 0, 1, cat="Binary")
y = LpVariable.dicts("y", quirofanos, 0, 1, cat="Binary")

# Función objetivo
model += lpSum(y[j] for j in quirofanos)

# Restricciones
# Cada operación debe ser asignada a un único quirófano
for i in operaciones:
    model += lpSum(x[(i, j)] for j in quirofanos) == 1

# Restricciones de incompatibilidades
for (i, h) in incompatibles:
    for j in quirofanos:
        model += x[(i, j)] + x[(h, j)] <= y[j]

# No se puede usar un quirófano si no está abierto
for i in operaciones:
    for j in quirofanos:
        model += x[(i, j)] <= y[j]

# Resolver el modelo
model.solve()

# Resultados
print(f"Número de quirófanos abiertos: {sum(y[j].value() for j in quirofanos)}")
for j in quirofanos:
    if y[j].value() == 1:
        operaciones_asignadas = [i for i in operaciones if x[(i, j)].value() == 1]
        print(f"Quirófano {j}: {operaciones_asignadas}")
