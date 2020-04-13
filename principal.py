# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: principal.py - flujo principal del proyecto
# -- mantiene: Natasha Gamez
# -- repositorio: https://github.com/NatashaGamez/Lab_2_LNGO
# -- ------------------------------------------------------------------------------------ -- #

import funciones as fn
#Datos
datos = fn.f_leer_archivo(param_archivo='archivo_tradeview_1.xlsx')
#Pip size
pip_size = fn.f_pip_size(param_ins='eurusd')
#Tranformaciones de tiempo
datos = fn.f_columnas_tiempos(param_data=datos)
#Transformaciones Pips
datos = fn.f_columnas_pips(param_data=datos)
# Estadisticas basicas y Raking
[df_1_tabla, df_1_ranking]  = fn.f_estadisticas_ba(param_data=datos)
# Capital acumulado
datos= fn.capital_acm(param_data=datos)
# Profit diario, profit diario opercaiones buy, profit diario opercaiones sell
[df_profit_d, profit_d_acm_c, profit_d_acm_v] = fn.f_profit_diario(param_data=datos)
# Medidas de Atribución al Desempeño (MAD)
Est_MAD = fn.f_estadisticas_mad(df_profit_d,profit_d_acm_c,profit_d_acm_v)
# Segos cognitivos
df_be_de = fn.f_be_de(datos)


