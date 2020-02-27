# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: funciones.py - funciones generales para uso en el proyecto
# -- mantiene: Natasha Gamez
# -- repositorio: https://github.com/NatashaGamez/Lab_2_LNGO
# -- ------------------------------------------------------------------------------------ -- #

import pandas as pd


# -- --------------------------------------------------- FUNCION: Leer archivo de entrada -- #
# -- ------------------------------------------------------------------------------------ -- #
# --

def f_leer_archivo(param_archivo):
    """
    Parameters
    ----------
    param_archivo : str : nombre de archivo a leer
    Returns
    -------
    df_data : pd.DataFrame : con informacion contenida en archivo leido
    Debugging
    ---------
    param_archivo = 'archivo_tradeview_1.xlsx'
    """

    df_data = pd.read_excel('archivos/' + param_archivo, sheet_name='Hoja1')

    return df_data