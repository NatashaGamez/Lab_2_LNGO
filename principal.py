# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: principal.py -
# -- mantiene: Natasha Gamez
# -- repositorio: https://github.com/NatashaGamez/Lab_2_LNGO
# -- ------------------------------------------------------------------------------------ -- #

import funciones as fn

datos = fn.f_leer_archivo(param_archivo='archivo_tradeview_1.xlsx')
pip_size = fn.f_pip_size(param_ins='eurusd')
datos = fn.f_columnas_datos(param_data=datos)
