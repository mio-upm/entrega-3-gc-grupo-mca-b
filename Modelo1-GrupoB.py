# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 12:38:53 2024

"""
import pulp as lp
import pandas as pd

df_costes = pd.read_excel("241204_costes.xlsx", index_col = 0)
df_operaciones = pd.read_excel("241204_datos_operaciones_programadas.xlsx", index_col = 0)

equipos_cardiologia_pediatrica = df_operaciones[df_operaciones["Especialidad quirúrgica"]=="Cardiología Pediátrica"]
equipos_medicos = equipos_cardiologia_pediatrica.loc[:,'Equipo de Cirugía']

quirofanos = df_costes.index

#C = {(i, j): [df_costes.loc[i, j] for i in equipos_cardiologia_pediatrica for j in str(df_costes.index)]}

# Los costes se encuentran en la matriz de costes y se filtran al llamar al conjunto de cardiologia pediatrica


