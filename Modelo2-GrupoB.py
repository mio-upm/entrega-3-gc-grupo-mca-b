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
    
'''
def generar_planificaciones(operaciones):
  planificaciones = []  # Lista de quirófanos con operaciones asignadas
    
  for op in sorted(operaciones, key=lambda x: x["Hora inicio "]):
       asignado = False
       for quir in planificaciones:
            # Si la operación no se solapa, se asigna al quirófano actual
            if all(op["Hora inicio "] >= q["Hora fin"] or op["Hora fin"] <= q["Hora inicio "] for q in quir):
                quir.append(op)
                asignado = True
                break
        
            if not asignado:
                # Si no se puede asignar, abre un nuevo quirófano
                planificaciones.append([op])
       return planificaciones

# Generar planificaciones

resultados = generar_planificaciones(equipos_filtrados)
'''
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
        '''
        while not asignado: 
            if activados == []:
                asignado = True
                quiro_elegido = quirofanos[0]
                K[quiro_elegido] = [ (codigo, t_inicio, t_fin) ]
        '''    
          
        i=0
        while i < len(activados) and not asignado:
            quiro = activados[i]
            if K[quiro][2] <= t_inicio:
               #libre
               asignado = True
               K[quiro].append( (codigo, t_inicio, t_fin) )
            else: i++
        
        if not asignado: #nuevo
            asignado = True
            quiro = quirofanos[num_activados]
            K[quiro] = [ (codigo, t_inicio, t_fin) ]
            activados.append(quiro)
            num_activados ++
   
            
'''
        asignado = False
        # monitora que quirofano esta libre (t inicio > tiempos[q])
        #for quiro,  in ocupado.items():
        while asignado == False:
            if ocupado == {}: 
                #vamos por quirofano1
            
            for quiro,lista in K.items():
                if K[quiro]
            
            
            if ocupado[quiro] < t_inicio:
                #libre 
                
        # guarda en K -> guarda numero op o conjunto 0/1 ?
        # actualiza tiempos para Q
'''  
    



'''

# Mostrar resultados
for idx, quir in enumerate(resultados):
    print(f"Quirófano {idx + 1}:")
    for op in quir:
        print(f"  {op['id']} - Inicio: {op['inicio']} - Fin: {op['fin']}")



'''







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


'''  
