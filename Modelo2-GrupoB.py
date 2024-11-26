# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 15:47:47 2024

"""
import pandas as pd
import pulp as lp
from datetime import datetime, timedelta

df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)

equipos_filtrados = df_operaciones[
    (df_operaciones['Especialidad quirúrgica'] == 'Cardiología Pediátrica') |
    (df_operaciones['Especialidad quirúrgica'] == 'Cirugía Cardíaca Pediátrica') |
    (df_operaciones['Especialidad quirúrgica'] == 'Cirugía Cardiovascular') |
    (df_operaciones['Especialidad quirúrgica'] == 'Cirugía General y del Aparato Digestivo')
]
#equipos_medicos = equipos_filtrados.loc[:,'Equipo de Cirugía']








# Datos de ejemplo: [id, inicio, fin]
#operaciones = [
    #{"id": "OP1", "inicio": datetime(2024, 12, 4, 13, 10), "fin": datetime(2024, 12, 4, 15, 15)},
    #{"id": "OP2", "inicio": datetime(2024, 12, 4, 18, 15), "fin": datetime(2024, 12, 4, 19, 40)},
    #{"id": "OP3", "inicio": datetime(2024, 12, 4, 15, 30), "fin": datetime(2024, 12, 4, 17, 0)},
    #{"id": "OP4", "inicio": datetime(2024, 12, 4, 14, 0), "fin": datetime(2024, 12, 4, 16, 0)}]
    

def generar_planificaciones(operaciones):
  planificaciones = []  # Lista de quirófanos con operaciones asignadas
    
    for op in sorted(operaciones, key=lambda x: x["inicio"]):
        asignado = False
        for quir in planificaciones:
            # Si la operación no se solapa, se asigna al quirófano actual
            if all(op["inicio"] >= q["fin"] or op["fin"] <= q["inicio"] for q in quir):
                quir.append(op)
                asignado = True
                break
        
        if not asignado:
            # Si no se puede asignar, abre un nuevo quirófano
            planificaciones.append([op])
    
    return planificaciones

# Generar planificaciones
resultados = generar_planificaciones(operaciones)

# Mostrar resultados
for idx, quir in enumerate(resultados):
    print(f"Quirófano {idx + 1}:")
    for op in quir:
        print(f"  {op['id']} - Inicio: {op['inicio']} - Fin: {op['fin']}")











#Definir parametros
coste_medio = []
for i in df_costes.columns: 
    suma_costes = df_costes[i].sum()
    media = suma_costes/len(df_costes.index)
    coste_medio.append((i, media))
    
B_ik = {}
for i in equipos_medicos.index:
    for k in ZAPATILLA:
        B_ik[(i,k)] == 1 if i in ZAPATILLA else 0
        
#Definir problema
problema = lp.LpProblem("Entrega 3 Modelo 2", lp.LpMinimize)
    
#Definir variables 
y = lp.LpVariable.dicts("y", k, cat = lp.LpBinary)

#Funcion objetivo 
problema += lp.lpSum(C_k[(k)]*y[(k)] for k in ZAPATILLA)

#Restriccion 1
for i in equipos_medicos.index:
    problema += lp.lpSum(B_ik[(i, k)] * y[k] for j in ZAPATILLA) >= 1


    
