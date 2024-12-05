# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 09:49:18 2024

@author: GrupoB
"""
import pulp as lp
import pandas as pd

df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)

quirofanos = df_costes.index.tolist()
operaciones = df_operaciones

#%% CONDICIONES INICIALES
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
            
    #quitar los vacios
    K_final = {}
    for key, val in K.items():
        if val != []:
            K_final[key] = [codigo for codigo, tiempoI, tiempoF in val]
    return K_final


def Bik(operaciones, planificaciones):
    B_ik={}
    count = 0
    for k in planificaciones.keys(): #quirofanos
        for i in operaciones.index: #codigo operacion
            if i in planificaciones[k]:
                B_ik[(i,k)] = 1
                count += 1
            else: B_ik[(i,k)]= 0
    return B_ik

#%% MAESTRO RELAJADO
def maestro_relajado(operaciones, planificaciones):
    #Definir problema
    problema = lp.LpProblem("Entrega3_Maestro_Relajado", lp.LpMinimize)
    B_ik=Bik(operaciones, planificaciones)  
    codigos = operaciones.index.tolist()
    #Definir variables 
    x = lp.LpVariable.dicts("x", [k for k in planificaciones.keys()], lowBound=0, cat = lp.LpContinuous)

    #Funcion objetivo 
    problema += lp.lpSum(x[(k)] for k in planificaciones.keys())

    #Restriccion 
    for i in codigos:
        problema += lp.lpSum(B_ik[(i, k)] * x[k] for k in planificaciones.keys()) >= 1

    #resolución
    #ahora queremos sacar de esta función los precios sombra
    problema.solve(lp.PULP_CBC_CMD(msg=False))
    
    precios_sombra = {}
    for name,c in zip(codigos, problema.constraints.values()):
        precios_sombra[name] = c.pi
    
    return problema.objective.value(), precios_sombra

#%% GENERACIÓN DE COLUMNAS
def conflictos(df_operaciones):
    # Crear el diccionario de incompatibilidades
    L = {x: [] for x in df_operaciones.index}

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
                    L[codigo_a].append(codigo_b)
                    L[codigo_b].append(codigo_a)
            else:
                if b_fin > a_inicio:  # Incompatible
                    L[codigo_a].append(codigo_b)
                    L[codigo_b].append(codigo_a)
    return L

#%%
def problema_dual(operaciones, precio_sombra, incompatibles):
    # buscamos generacion de combinacion de operaciones
    #precio_sombra = diccionario { operacion: precioS    }
    #operaciones = dataFrame de operaciones
    codigos = operaciones.index.tolist() #los codigos de las operaciones
    W=1 #longitud
    
    problema_dual = lp.LpProblem("Entrega3_Modelo_dual", lp.LpMaximize)
    y = lp.LpVariable.dicts("y",codigos, cat="Binary") #todavia relajado
     
    #funcion objectivo
    problema_dual += lp.lpSum(y[i]* precio_sombra[i] for i in codigos)   
    
    #restricciones   
    for i in codigos:
        for j in incompatibles[i]:
            problema_dual+= y[i]+y[j]<=W
        
    problema_dual.solve(lp.PULP_CBC_CMD(msg=False))
    f_objectivo = problema_dual.objective.value()

    lista_solver = [v.name.split('_')[1]+" "+v.name.split('_')[2]+"-"+v.name.split('_')[3] for v in problema_dual.variables() if v.varValue > 0]

    return f_objectivo, lista_solver


#%% MAESTRO SIN RELAJAR
def maestro(operaciones, planificaciones):
    #Definir problema
    problema = lp.LpProblem("Entrega3_Maestro", lp.LpMinimize)
    B_ik=Bik(operaciones, planificaciones)  
    #Definir variables 
    x = lp.LpVariable.dicts("x", [k for k in planificaciones.keys()], lowBound=0, cat = lp.LpInteger)

    #Funcion objetivo 
    problema += lp.lpSum(x[(k)] for k in planificaciones.keys())

    #Restriccion 1
    for i in operaciones.index:
        problema += lp.lpSum(B_ik[(i, k)] * x[k] for k in planificaciones.keys()) >= 1

    #resolución
    problema.solve(lp.PULP_CBC_CMD(msg=False))

    return problema.objective.value()


#%% MAIN
planificacion= planificación_inicial(operaciones, quirofanos)
incompatibles = conflictos(operaciones)

num_iteraciones=0
iter_max=5 #ultima vez ha llegado hasta iteracion 23
fobj_dual = 40

while num_iteraciones< iter_max and fobj_dual>1:
    
    sol_maestro, precio_sombra = maestro_relajado(operaciones, planificacion)
    
    #crear nueva f obj para generación de columnas y actualizar fobj 
    fobj_dual, nueva_planif= problema_dual(operaciones, precio_sombra, incompatibles)
    print(num_iteraciones,": ", sol_maestro, "  ", fobj_dual,"  ", nueva_planif)
    
    num_iteraciones += 1
    
    #poner planificaciones
    nuevo_quirofano=len(planificacion)+1
    planificacion['Quirofano '+str(nuevo_quirofano)]=nueva_planif

'''
#issue: como verificar quien hace que? pq creo q si usamos 94 quirofanos y tenemos 100 en diccionario, no esta bien
monitor = { i:0 for i in operaciones.index.tolist()    }
for quiro in planificacion.keys():
    #check cuantas veces salen las operaciones
    for j in planificacion[quiro]:
        monitor[j] += 1
'''

sol_final = maestro(operaciones, planificacion)
print(sol_final)