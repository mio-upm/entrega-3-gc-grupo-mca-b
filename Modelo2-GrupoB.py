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
    (df_operaciones['Especialidad quirúrgica'] == 'Cirugía General y del Aparato Digestivo')].sort_values(by='Hora inicio ')


# Datos de ejemplo: [id, inicio, fin]
#operaciones = [
    #{"id": "OP1", "inicio": datetime(2024, 12, 4, 13, 10), "fin": datetime(2024, 12, 4, 15, 15)},
    #{"id": "OP2", "inicio": datetime(2024, 12, 4, 18, 15), "fin": datetime(2024, 12, 4, 19, 40)},
    #{"id": "OP3", "inicio": datetime(2024, 12, 4, 15, 30), "fin": datetime(2024, 12, 4, 17, 0)},
    #{"id": "OP4", "inicio": datetime(2024, 12, 4, 14, 0), "fin": datetime(2024, 12, 4, 16, 0)}]
    

# contenedor K = { quirofanos : [(op1, inicio, fin), (op2...)]   }

#hay que ordenar operaciones 
def nueva_planificacion(operaciones, costes):  #dataframes con operac ordenadas
    #objectivo es generar un conjunto de planificacion K
    quirofanos = costes.index
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
            K_final = {}
    for key, val in K.items():
        if val != []:
            K_final[key] = val
    return K_final


prueba=nueva_planificacion(df_operaciones, df_costes)


equipos_medicos=equipos_filtrados['Equipo de Cirugía']   
planificaciones=nueva_planificacion(equipos_filtrados, df_costes)
      
'''

# Mostrar resultados
for idx, quir in enumerate(resultados):
    print(f"Quirófano {idx + 1}:")
    for op in quir:
        print(f"  {op['id']} - Inicio: {op['inicio']} - Fin: {op['fin']}")

'''

#Definir parametros
coste_medio = {}
for i in df_costes.columns: 
    suma_costes = df_costes[i].sum()
    media = round(suma_costes/len(df_costes.index),2)
    coste_medio[i]= round(media,2)
   
    
B_ik = {}


for i in equipos_medicos.index:
    for k in planificaciones.keys():
        long=len(planificaciones[k])
        lista_operaciones= [planificaciones[k][j][0] for j in range (long)]
        if i in lista_operaciones:
            B_ik[(i,k)] = 1 
        else: 
            B_ik[(i,k)] = 0

  
C_k={}

for k in planificaciones.keys():
    C_k[k]=0
    for i in equipos_medicos.index:
        C_k[k]=C_k[k]+round(coste_medio[i]*B_ik[(i,k)],2)
    
#Definir problema
problema = lp.LpProblem("Entrega_Modelo_2", lp.LpMinimize)
    
#Definir variables 
y = lp.LpVariable.dicts("y", [k for k in planificaciones.keys()], cat = lp.LpBinary)

#Funcion objetivo 
problema += lp.lpSum(C_k[(k)]*y[(k)] for k in planificaciones.keys())

#Restriccion 1
for i in equipos_medicos.index:
    problema += lp.lpSum(B_ik[(i, k)] * y[k] for k in planificaciones.keys()) >= 1


problema.solve(lp.PULP_CBC_CMD(msg=False))

valor_solucion=problema.objective.value()

print(f'El coste de la planificación es de {valor_solucion}')
print('\n')
print('Los quirófanos abiertos con las siguientes planificaciones:')

count = 0
for v in problema.variables():
    if v.varValue >0:
        count += 1
        quiro_nombre= v.name.split('_')[1]+" "+v.name.split('_')[2]
        plani_quiro=planificaciones[quiro_nombre]
        print(quiro_nombre,":",plani_quiro )
        
print('\n')
print(f'Se abrirán {count} quirófanos')


