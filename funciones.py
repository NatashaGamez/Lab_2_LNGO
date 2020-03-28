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
    param_archivo = 'archivo_1_LNGO.xlsx'
    """

    df_data = pd.read_excel('archivos/' + param_archivo, sheet_name='Hoja1')

    # convertir nombre de columnas en minusculas
    df_data.columns = [list(df_data.columns)[i].lower()
                       for i in range(0, len(df_data.columns))]
    # elegir solo reglones donde "type" == buy | sell
    df_data = df_data.drop(df_data[df_data['type'] == 'balance'].index)
    df_data = df_data.drop(df_data[df_data['type'] == 'buy limit'].index)
    df_data = df_data.drop(df_data[df_data['type'] == 'sell limit'].index)

    # asegurar que ciertas columnas son tipo numerico
    numcols = ['s/l', 't/p', 'commission', 'openprice', 'closeprice', 'profit', 'size', 'swap',
               'taxes', 'order']
    df_data[numcols] = df_data[numcols].apply(pd.to_numeric)

    # asegurar que ticekr no tenga -2
    df_data['symbol'] = [df_data.iloc[i, 4].replace("-2", "") for i in range(df_data.shape[0])]

    return df_data


def f_pip_size(param_ins):
    """

    Parameters
    ----------
    param_ins : str : nombre de instrumento
    Returns
    -------
    Debugging
    """
    # encontar y eliminar un guion bajo
    inst = param_ins.replace('-', '')

    # transformar a minusculas
    inst = inst.lower()

    # lista de pips por instrumento
    pip_inst = {'usdjpy': 100, 'gbpjpy': 100, 'eurjpy': 100, 'cadjpy': 100,
                'chfjpy': 100,
                'eurusd': 10000, 'gbpusd': 10000, 'usdcad': 10000, 'usdmxn': 10000,
                'audusd': 10000, 'nzdusd': 10000, 'usdchf': 10000, 'eurgbp': 10000,
                'eurchf': 10000, 'eurnzd': 10000, 'euraud': 10000, 'gbpnzd': 10000,
                'gbpchf': 10000, 'gbpaud': 10000, 'audnzd': 10000, 'nzdcad': 10000,
                'audcad': 10000, 'gbpcad': 10000, 'xauusd': 10, 'xagusd': 10, 'btcusd': 1}

    return pip_inst[inst]


def f_columnas_tiempos(param_data):
    """
    Parameters
    ----------
    param_data : DataFrame base
    Returns
    -------
    df_data : pd.DataFrame : con informacion contenida en archivo leido
    Debugging
    ---------
    """
    # convertir columna de 'closetime' y 'opentime' utilizando pd.to_datatime
    param_data['closetime'] = pd.to_datetime(param_data['closetime'])
    param_data['opentime'] = pd.to_datetime(param_data['opentime'])

    # tiempo transcurrido de una operación
    param_data['tiempo'] = [(param_data.loc[i, 'closetime'] -
                             param_data.loc[i, 'opentime']).delta / 1e9
                            for i in range(0, len(param_data['closetime']))]

    return param_data['tiempo']


def f_columnas_pips(param_data):
    """
    Parameters
    ----------
    param_data : DataFrame base
    Returns
    -------
    df_data : pd.DataFrame : con informacion contenida en archivo leido
    Debugging
    ---------
    """
    param_data['pips'] = param_data.iloc[:, 0]
    param_data['pips_acm'] = param_data.iloc[:, 14]
    param_data['profit_acm'] = param_data.iloc[:, 13]
    for i in range(param_data.shape[0]):
        # Pips por operacion
        if param_data.iloc[i, 2] == 'buy':
            param_data['pips'][i] = (param_data.iloc[i, 9] - param_data.iloc[i, 5]) \
                                    * f_pip_size(param_ins=param_data.iloc[i, 4])
        else:
            param_data['pips'][i] = (param_data.iloc[i, 5] - param_data.iloc[i, 9]) \
                                    * f_pip_size(param_ins=param_data.iloc[i, 4])

        # Pips acumulados
        param_data['pips_acm'][i] = param_data.iloc[i, 14]
        if i > 0:
            param_data['pips_acm'][i] = param_data.iloc[i - 1, 15] + param_data.iloc[i, 14]

        # Profit acumulado
        param_data['profit_acm'][i] = param_data.iloc[i, 13]
        if i > 0:
            param_data['profit_acm'][i] = param_data.iloc[i - 1, 16] + param_data.iloc[i, 13]

    return param_data


def f_estadisticas_ba(param_data):
    """
    Parameters
    ----------
    :param param_data:
    Returns
    -------
    :return: df_1_tabla y df_2_ranking
    """
    # Construccion de df_1_tabla
    rows = {'Name':['Ops totales', 'Ganadoras', 'Ganadoras_c', 'Ganadoras_v',
                      'Perdedoras', 'Perdedoras_c', 'Perdedoras_v', 'Media(Profit)',
                      'Media(Pips)', 'r_efectividad', 'r_proporcion', 'r_efectividad_v',
                      'r_efectividad_c']}
    df_1_tabla = pd.DataFrame(rows)
    df_1_tabla['Valor'] = df_1_tabla.iloc[:, 0]
    df_1_tabla.iloc[0, 1] = param_data.shape[0]
    win = 0
    lose = 0
    buy = 0
    sell = 0
    buy_l = 0
    sell_l = 0
    for i in range(param_data.shape[0]):
        if param_data.iloc[i, 13] >= 0:
            win = win + 1
            if param_data.iloc[i, 2] == 'buy':
                buy = buy + 1
            else:
                sell = sell + 1
        else:
            lose = lose + 1
            if param_data.iloc[i, 2] == 'buy':
                buy_l = buy_l + 1
            else:
                sell_l = sell_l + 1
    df_1_tabla.iloc[1, 1] = win
    df_1_tabla.iloc[2, 1] = buy
    df_1_tabla.iloc[3, 1] = sell
    df_1_tabla.iloc[4, 1] = lose
    df_1_tabla.iloc[5, 1] = buy_l
    df_1_tabla.iloc[6, 1] = sell_l
    df_1_tabla.iloc[7, 1] = param_data.iloc[:, 13].median()
    df_1_tabla.iloc[8, 1] = param_data.iloc[:, 14].median()
    df_1_tabla.iloc[9, 1] = df_1_tabla.iloc[1, 1] / df_1_tabla.iloc[0, 1]
    df_1_tabla.iloc[10, 1] = df_1_tabla.iloc[1, 1] / df_1_tabla.iloc[4, 1]
    df_1_tabla.iloc[11, 1] = df_1_tabla.iloc[2, 1] / df_1_tabla.iloc[0, 1]
    df_1_tabla.iloc[12, 1] = df_1_tabla.iloc[3, 1] / df_1_tabla.iloc[0, 1]
    
    return df_1_tabla
