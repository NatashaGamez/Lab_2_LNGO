# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: funciones.py - procesamiento de datos
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

    # convertir nombre de columnas en minusculas
    df_data.columns = [list(df_data.columns)[i].lower()
                       for i in range(0, len(df_data.columns))]

    # asegurar que ciertas columnas son tipo numerico
    numcols = ['s/l', 't/p', 'commission', 'openprice', 'closeprice', 'profit', 'size', 'swap',
               'taxes', 'order']

    df_data[numcols] = df_data[numcols].apply(pd.to_numeric)
    return df_data
