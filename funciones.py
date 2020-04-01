# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: funciones.py - procesamiento de datos
# -- mantiene: Natasha Gamez
# -- repositorio: https://github.com/NatashaGamez/Lab_2_LNGO
# -- ------------------------------------------------------------------------------------ -- #

import pandas as pd
import numpy as np

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
    param_data.iloc[:, 8] = pd.to_datetime(param_data['closetime'])
    param_data.iloc[:, 1] = pd.to_datetime(param_data['opentime'])

    # tiempo transcurrido de una operación
    param_data['tiempo'] = [(param_data.loc[i, 'closetime'] -
                             param_data.loc[i, 'opentime']).delta / 1e9
                            for i in range(0, len(param_data['closetime']))]

    return param_data


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
    param_data['pips_acm'] = param_data.iloc[:, 15]
    param_data['profit_acm'] = param_data.iloc[:, 14]
    for i in range(param_data.shape[0]):
        # Pips por operacion
        if param_data.iloc[i, 2] == 'buy':
            param_data['pips'][i] = (param_data.iloc[i, 9] - param_data.iloc[i, 5]) \
                                    * f_pip_size(param_ins=param_data.iloc[i, 4])
        else:
            param_data['pips'][i] = (param_data.iloc[i, 5] - param_data.iloc[i, 9]) \
                                    * f_pip_size(param_ins=param_data.iloc[i, 4])

        # Pips acumulados
        param_data['pips_acm'][i] = param_data.iloc[i, 15]
        if i > 0:
            param_data['pips_acm'][i] = param_data.iloc[i - 1, 16] + param_data.iloc[i, 15]

        # Profit acumulado
        param_data['profit_acm'][i] = param_data.iloc[i, 13]
        if i > 0:
            param_data['profit_acm'][i] = param_data.iloc[i - 1, 17] + param_data.iloc[i, 13]

    return param_data


def f_estadisticas_ba(param_data):
    """
    Parameters
    ----------
    :param param_data: DataFrame base
    Returns
    -------
    :return: df_1_tabla y df_2_ranking
    """
    # Construccion de df_1_tabla
    rows = {'Name': ['Ops totales', 'Ganadoras', 'Ganadoras_c', 'Ganadoras_v',
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

    # -- -------------------------------------------------------------------------------- -- #
    # df_1_ranking
    # lista instrumento
    inst = ['usdjpy', 'gbpjpy', 'eurjpy', 'cadjpy', 'chfjpy', 'eurusd', 'gbpusd',
            'usdcad', 'usdmxn', 'audusd', 'nzdusd', 'usdchf', 'eurgbp', 'eurchf',
            'eurnzd', 'euraud', 'gbpnzd', 'gbpchf', 'gbpaud', 'audnzd', 'nzdcad',
            'audcad', 'gbpcad', 'xauusd', 'xagusd', 'btcusd']

    # contar repeticiones de symbolo y numero de movimientos ganadores
    rep = []
    rank = []
    for i in inst:
        count = 0
        win = 0
        for k in range(param_data.shape[0]):
            if i in param_data.iloc[k, 4]:
                count = count + 1
                if param_data.iloc[k, 13] > 0:
                    win = win + 1

        rep.append(count)
        rank.append(win)

    # Formar tabla
    df_1_ranking = pd.DataFrame(list(zip(inst, rep, rank)))
    df_1_ranking.columns = ['Symbol', 'Rep', '#ganadora']
    df_1_ranking = df_1_ranking.drop(df_1_ranking[df_1_ranking.iloc[:, 2] == 0].index)
    df_1_ranking = df_1_ranking.reset_index(drop=True)
    df_1_ranking['Rank %'] = 0
    for i in range(df_1_ranking.shape[0]):
        df_1_ranking['Rank %'][i] = df_1_ranking.iloc[i, 2] / df_1_ranking.iloc[i, 1] * 100
    df_1_ranking = df_1_ranking.drop(['Rep'], axis=1)
    df_1_ranking = df_1_ranking.drop(['#ganadora'], axis=1)
    df_1_ranking = df_1_ranking.sort_values('Rank %', ascending=False)
    df_1_ranking = df_1_ranking.reset_index(drop=True)

    return df_1_tabla, df_1_ranking


def capital_acm(param_data):
    """
    Parameters
    ----------
    :param param_data: DataFrame base
    Returns
    -------
    :return: param_data
    """
    param_data['capital_acm'] = param_data.iloc[:, 17] + 5000

    return param_data


def f_profit_diario(param_data):
    """
    Parameters
    ----------
    :param param_data: DataFrame base
    Returns
    -------
    :return: df_profit
    """
    # Extraer datos necesarios y acomodarlos
    Profit = param_data.iloc[:, [1, 13, 13]]
    Profit.columns = ['Timestamp', 'Profit_d', 'Profit_acm_d']
    Profit['Timestamp'] = [param_data.iloc[i, 1].date() for i in range(param_data.shape[0])]
    Profit = Profit.sort_values('Timestamp', ascending=True)
    Profit = Profit.reset_index(drop=True)
    # número de movimiento final en día
    valor_fin = []
    for i in range(Profit.shape[0]):
        if i < 83:
            if Profit['Timestamp'][i] != Profit['Timestamp'][i + 1]:
                valor_fin.append(i)
        if i == 83:
            valor_fin.append(i)
    # sacar fechas de días de movimientos y número de moviemientos en ese día
    dias = []
    mov = [valor_fin[0] + 1]
    for k in range(len(valor_fin)):
        dias.append(Profit['Timestamp'][valor_fin[k]])
        if k > 0:
            r = valor_fin[k] - valor_fin[k - 1]
            mov.append(r)
    # profit por dia
    profit = []
    suma = 0
    for e in range(len(valor_fin)):
        if e == 0:
            j = Profit.iloc[e:valor_fin[e] + 1, 1]
            suma = j.sum(axis=0)
        else:
            j = Profit.iloc[valor_fin[e - 1] + 1:valor_fin[e] + 1, 1]
            suma = j.sum(axis=0)
        profit.append(suma)
    # juntar en tabla
    df_profit = pd.DataFrame(list(zip(dias, mov, profit)))
    df_profit.columns = ['Timestamp', 'mov por día', 'Profit_d']
    # profit diario acumulado
    df_profit['Profit_acm_d'] = df_profit.iloc[:, 2]+5000
    for a in range(df_profit.shape[0]):
        df_profit['Profit_acm_d'][a] = df_profit['Profit_acm_d'][a]
        if a > 0:
            df_profit['Profit_acm_d'][a] = df_profit['Profit_acm_d'][a - 1] \
                                           + df_profit['Profit_acm_d'][a]-5000
    return df_profit
def f_estadisticas_mad(param_data):
    """
    Parameters
    ----------
    :param param_data: DataFrame base
    Returns
    -------
    :return: df_mad

    """
    pr = param_data['Profit_acm_d']
    rp = np.diff(np.log(pr))
    # Sharpe Ratio
    rf = 0.08
    std_sharpe= np.std(rp)
    sharpe = np.mean(rp - rf) / std_sharpe

    # Sortino Ratio (Posiciones Compra)
    a = []
    mar = 0.3 / 252
    for i in range(len(rp)):
        if rp[i] < 0:
            a.append(i)
    std_sortinoc = np.std(np.delete(rp, a))
    sortino_c = np.mean(rp - mar) / std_sortinoc

    # Sortino Ratio (Posiciones Venta)
    g = []
    for i in range(len(rp)):
        if rp[i] > 0:
            g.append(i)
    std_sortinov = np.std(np.delete(rp, g))
    sortino_v = np.mean(rp - mar) / std_sortinov

    # Tabla
    df_mad = {'Metrica': ['Sharpe','Sortino_C','Sortino_V'],
    'Valor': [sharpe,sortino_c,sortino_v]}
    df_mad = pd.DataFrame(df_mad)
    return df_mad
