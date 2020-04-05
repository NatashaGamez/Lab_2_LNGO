# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: principal.py -
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
# Profit diario
Prfit_d = fn.f_profit_diario(param_data=datos)
