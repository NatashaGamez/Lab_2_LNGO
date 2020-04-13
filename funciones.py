# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: funciones.py - procesamiento de datos
# -- mantiene: Natasha Gamez
# -- repositorio: https://github.com/NatashaGamez/Lab_2_LNGO
# -- ------------------------------------------------------------------------------------ -- #

import pandas as pd
import numpy as np
import datetime
import fun_precios_m as fpm
from datos import OA_Ak



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
    df_data = df_data.reset_index(drop=True)

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
                            for i in range(param_data.shape[0])]

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
    # contar ganadoras, perdedoras y las ques son de buy o sell
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
    # Inclusion de datos en tabla
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
    Profit = param_data.iloc[:, [2, 8, 13, 13]]
    Profit.columns = ['Tipo', 'Timestamp', 'Profit_d', 'Profit_acm_d']
    Profit['Timestamp'] = [Profit['Timestamp'][i].date() for i in range(param_data.shape[0])]
    Profit = Profit.sort_values('Timestamp', ascending=True)
    Profit = Profit.reset_index(drop=True)

    # Sacar todas las fechas incluso en donde no se hizo movimiento
    day = Profit['Timestamp'][0]
    day_fin = Profit['Timestamp'][Profit.shape[0] - 1]
    one_day = datetime.timedelta(days=1)
    days = []
    for x in range((day_fin - day).days):
        day_new = day + one_day * x
        days.append(day_new)
    days.append(day_fin)
    # dias en string
    days = [days[l].strftime("%Y-%m-%d") for l in range(len(days))]

    # número (indice) de movimiento final en día
    valor_fin = []
    for i in range(Profit.shape[0]):
        if i < (Profit.shape[0] - 1):
            if Profit['Timestamp'][i] != Profit['Timestamp'][i + 1]:
                valor_fin.append(i)
        if i == (Profit.shape[0] - 1):
            valor_fin.append(i)
    # sacar fechas de días de movimientos y número de moviemientos en ese día
    dias = []
    mov = [valor_fin[0] + 1]
    for k in range(len(valor_fin)):
        dias.append(Profit['Timestamp'][valor_fin[k]])
        if k > 0:
            r = valor_fin[k] - valor_fin[k - 1]
            mov.append(r)
    dias = [dias[k].strftime("%Y-%m-%d") for k in range(len(dias))]

    # profit por dia
    profit = []
    suma = 0
    for e in range(len(valor_fin)):
        if e == 0:
            j = Profit.iloc[e:valor_fin[e] + 1, 2]
            suma = j.sum(axis=0)
        else:
            j = Profit.iloc[valor_fin[e - 1] + 1:valor_fin[e] + 1, 2]
            suma = j.sum(axis=0)
        profit.append(suma)
    # -- -------------------------------------------------------------------------------- -- #
    # profit solo operaciones buy por dia
    profit_c = []
    for x in range(len(valor_fin)):
        c = []
        for z in range(Profit.shape[0]):
            if x == 0 and Profit['Tipo'][z] == 'buy' and z <= valor_fin[x]:
                c.append(Profit['Profit_d'][z])
            if x > 0 and Profit['Tipo'][z] == 'buy' and valor_fin[x - 1] < z <= valor_fin[x]:
                c.append(Profit['Profit_d'][z])
            suma_c = np.sum(np.array(c))
        profit_c.append(suma_c)

    # profit solo operaciones sell por dia
    profit_v = []
    for x in range(len(valor_fin)):
        v = []
        for z in range(Profit.shape[0]):
            if x == 0 and Profit['Tipo'][z] == 'sell' and z <= valor_fin[x]:
                v.append(Profit['Profit_d'][z])
            if x > 0 and Profit['Tipo'][z] == 'sell' and valor_fin[x - 1] < z <= valor_fin[x]:
                v.append(Profit['Profit_d'][z])
            suma_v = np.sum(np.array(v))
        profit_v.append(suma_v)

    # Indentificar fechas sin moviemiento y agragarlas con profit 0
    a = []
    for ñ in dias:
        for m in range(len(days)):
            if ñ in days[m]:
                a.append(m)
    g = []
    for i in range(a[-1]):
        if i not in a:
            g.append(i)
    for s in range(len(g)):
        dias.append(days[g[s]])
        profit.append(0)
        profit_c.append(0)
        profit_v.append(0)
    # -- -------------------------------------------------------------------------------- -- #
    # Generar tabla de rendimiento diarios
    df_profit = pd.DataFrame(list(zip(dias, profit)))
    df_profit.columns = ['Timestamp', 'Profit_d']
    df_profit = df_profit.sort_values('Timestamp', ascending=True)
    df_profit = df_profit.reset_index(drop=True)
    # profit diario acumulado
    df_profit['Profit_acm_d'] = df_profit.iloc[:, 1] + 5000
    for a in range(df_profit.shape[0]):
        df_profit['Profit_acm_d'][a] = df_profit['Profit_acm_d'][a]
        if a > 0:
            df_profit['Profit_acm_d'][a] = df_profit['Profit_acm_d'][a - 1] \
                                           + df_profit['Profit_acm_d'][a] - 5000
    # -- -------------------------------------------------------------------------------- -- #
    # Generar tabla de rendimiento diarios solo movimientos buy
    df_c = pd.DataFrame(list(zip(dias, profit_c)))
    df_c.columns = ['Timestamp', 'Profit_d_c']
    df_c = df_c.sort_values('Timestamp', ascending=True)
    df_c = df_c.reset_index(drop=True)
    df_c['Profit_d_acm_c'] = df_c['Profit_d_c']
    for q in range(len(profit_c)):
        df_c['Profit_d_acm_c'][q] = df_c['Profit_d_c'][q] + 5000
        if q > 0:
            df_c['Profit_d_acm_c'][q] = df_c['Profit_d_c'][q] + df_c['Profit_d_acm_c'][q - 1]

    # -- -------------------------------------------------------------------------------- -- #
    # Generar tabla de rendimiento diarios solo movimientos sell
    df_v = pd.DataFrame(list(zip(dias, profit_v)))
    df_v.columns = ['Timestamp', 'Profit_d_v']
    df_v = df_v.sort_values('Timestamp', ascending=True)
    df_v = df_v.reset_index(drop=True)
    df_v['Profit_d_acm_v'] = df_v['Profit_d_v']
    for w in range(len(profit_v)):
        df_v['Profit_d_acm_v'][w] = df_v['Profit_d_v'][w] + 5000
        if w > 0:
            df_v['Profit_d_acm_v'][w] = df_v['Profit_d_v'][w] + df_v['Profit_d_acm_v'][w - 1]

    return df_profit, df_c, df_v


def f_estadisticas_mad(param_data, profit_acm_c, profit_acm_v):
    """
    Parameters
    ----------
    :param param_data: DataFrame base
    Returns
    -------
    :return: df_mad

    """

    # Sharpe Ratio
    pr = param_data['Profit_acm_d']
    rp = np.diff(np.log(pr))  # calculo de rendimiento
    rf = 0.08 / 300  # convertir tasa a diaria
    std_sharpe = np.std(rp)  # calculo de desviacion estandar
    sharpe = round(np.mean(rp - rf) / std_sharpe, 5)

    mar = 0.3 / 252
    # Sortino Ratio (Posiciones Compra)
    pr_c = profit_acm_c['Profit_d_acm_c']  # profit de operaciones diarias solo compra
    rp_c = np.diff(np.log(pr_c))  # rendimiento de operaciones diarias solo compra
    a = []
    for i in range(len(rp_c)):
        if rp_c[i] < mar:  # solo tomar los que son menores a nuestra meta
            a.append(rp_c[i])
    std_sortinoc = np.std(a)
    sortino_c = round(np.mean(rp_c - mar) / std_sortinoc, 4)

    # Sortino Ratio (Posiciones Venta)
    pr_v = profit_acm_v['Profit_d_acm_v']  # profit de operaciones diarias solo venta
    rp_v = np.diff(np.log(pr_v))  # rendimiento de operaciones diarias solo venta
    v = []
    for x in range(len(rp_v)):
        if rp_v[x] < mar:  # solo tomar los que son menores a nuestra meta
            v.append(rp_v[x])
    std_sortinov = np.std(v)
    sortino_v = round(np.mean(rp_v - mar) / std_sortinov, 4)

    # DrawDown
    elem = []
    # Encontrar donde se perdia
    for u in range(param_data.shape[0]):
        if u > 0:
            if param_data['Profit_acm_d'][u] < param_data['Profit_acm_d'][u - 1]:
                elem.append(u)
    e = [elem[0]]
    for t in range(len(elem)):  # calcular la fecha inicial y final
        if t > 0 and elem[t] - elem[t - 1] < 2:
            e.append(elem[t])
    if len(e) == 1:
        e.append(elem[-1])
        e.pop(0)
    DD = param_data['Profit_acm_d'][e[len(e) - 1]] - param_data['Profit_acm_d'][e[0]]
    if DD == 0:
        DD = param_data['Profit_d'][param_data.shape[0] - 1]
    DrawDown = [param_data['Timestamp'][e[0] - 1], param_data['Timestamp'][e[len(e) - 1]],
                round(DD, 2)]

    # DrawUP
    elem_up = []
    # Encontrar donde se ganaba
    for u in range(param_data.shape[0]):
        if u > 0:
            if param_data['Profit_acm_d'][u] > param_data['Profit_acm_d'][u - 1]:
                elem_up.append(u)
    up = []
    for p in range(len(elem_up)):  # calcular la fecha inicial y final
        if 0 == p < len(elem_up) and (elem_up[p + 1] - elem_up[p]) < 3:
            up.append(elem_up[p])
        if p > 0 and (elem_up[p] - elem_up[p - 1]) < 2 or (elem_up[p] - elem_up[p - 1]) > 3:
            up.append(elem_up[p])
    DU = param_data['Profit_acm_d'][up[len(up) - 1]] - param_data['Profit_acm_d'][up[0] - 1]
    DrawUp = [param_data['Timestamp'][up[0] - 1], param_data['Timestamp'][up[len(up) - 1]],
              round(DU, 2)]
    # -- -------------------------------------------------------------------------------- -- #
    # -- ----------------------------------------------------- Descargar precios de OANDA -- #
    one_day = datetime.timedelta(days=1)
    # token de OANDA
    OA_In = "SPX500_USD"  # Instrumento
    OA_Gn = "D"  # Granularidad de velas
    fini = pd.to_datetime(param_data['Timestamp'][1]).tz_localize('GMT')  # Fecha inicial
    ffin = pd.to_datetime(datetime.datetime.strptime(param_data['Timestamp'][param_data.shape[0] - 1],
                                                     '%Y-%m-%d') + one_day * 3).tz_localize('GMT')
    # Fecha final

    # Descargar precios masivos para bench mark
    df_pe = fpm.f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=OA_Gn,
                                  p3_inst=OA_In, p4_oatk=OA_Ak, p5_ginc=4900)
    # Sacar todas las fechas
    day = param_data['Timestamp'][0]
    day = datetime.datetime.strptime(day, '%Y-%m-%d')
    day_fin = param_data['Timestamp'][param_data.shape[0] - 1]
    day_fin = datetime.datetime.strptime(day_fin, '%Y-%m-%d')
    days = []
    for x in range((day_fin - day).days):
        day_new = day + one_day * x
        days.append(day_new)
    days.append(day_fin)
    days = [days[l].strftime("%Y-%m-%d") for l in range(len(days))]

    dias = df_pe['TimeStamp']
    dias = [dias[g].strftime("%Y-%m-%d") for g in range(len(dias))]

    # Indentificar fechas sin moviemiento y agragarlas poner profit 0
    a = []
    for ñ in dias:
        for m in range(len(days)):
            if ñ in days[m]:
                a.append(m)
    g = []
    for i in range(a[-1]):
        if i not in a:
            g.append(i)
    close = []
    for f in range(df_pe.shape[0]):
        close.append(df_pe['Close'][f])
    for s in range(len(g)):
        dias.append(days[g[s]])
        close.append(0)
    df = pd.DataFrame(list(zip(dias, close)))
    df.columns = ['Timestamp', 'Close']
    df = df.sort_values('Timestamp', ascending=True)
    df = df.reset_index(drop=True)

    # Poner precio igual anterior si es 0
    for i in range(len(df['Close'])):
        if df['Close'][i] == 0:
            df['Close'][i] = df['Close'][i - 1]

    # Information Ratio
    r_indice = np.diff(np.log(df['Close']))  # rendimiento
    info_ratio = np.mean(rp - r_indice) / np.std(rp - r_indice)

    # Tabla
    df_mad = {'Metrica': ['Sharpe', 'Sortino_C', 'Sortino_V', 'DrawDown', 'DrawUP',
                          'Information_r'],
              'Valor': [sharpe, sortino_c, sortino_v, DrawDown, DrawUp, info_ratio],
              'Descripción': ['Sharpe Ratio', 'Sortino Ratio para Posiciones de Compra',
                              'Sortino Ratio para Posiciones de Ventas', 'DrawDown De Capital',
                              'DrawUp de Capital', 'Information Ratio']}
    df_mad = pd.DataFrame(df_mad)

    return df_mad


def f_be_de(param_data):
    """
    Parameters
    ----------
    :param param_data: DataFrame base
    Returns
    -------
    :return: df

    """
    # Punto de referencia
    win = 0
    lose = 0
    c_g = 5000
    c_p = 5000
    i_cp = []  # indice de operacion perdedora
    i_cg = []  # indice de operacion ganadora
    capital_ganadora = []
    capital_perdedora = []
    # calcular capital ganadora y capital perdedora
    for i in range(param_data.shape[0]):
        if param_data.iloc[i, 13] >= 0:
            win = win + 1
            c_g = c_g + param_data.iloc[i, 13]
            capital_ganadora.append(c_g)
            capital_perdedora.append(5000)
            i_cg.append(i)
        else:
            lose = lose + 1
            c_p = c_p + param_data.iloc[i, 13]
            capital_ganadora.append(5000)
            capital_perdedora.append(c_p)
            i_cp.append(i)

    # calcular ratios
    r_cg = (capital_ganadora / param_data.iloc[:, -1]) * 100
    r_cp = (capital_perdedora / param_data.iloc[:, -1]) * 100
    r_cgcp = [(capital_perdedora[i] / capital_ganadora[i]) * 100 for i in range(len(r_cg))]

    # Aversion a la perdida
    df = {'capital': param_data.iloc[:, -1], 'capital_ganadora/capital_acm': r_cg,
          'capital_perdedora/capital_acm': r_cp, 'capital_perdedora/capital_ganadora': r_cgcp}
    df = pd.DataFrame(df)

    #  Verificar si cuando se cerro una operacion ganadora, habia abierta otra operacion con
    # perdida flotante
    ot = [param_data['opentime'][i].date() for i in range(param_data.shape[0])]
    ct = param_data['closetime']
    idx = []
    for i in range(param_data.shape[0]):
        for k in range(param_data.shape[0]):
            if ot[i] <= ot[k] and ct[i] < ct[k] and param_data['profit'][k] < 0 \
                    and param_data['profit'][i] > 0 and param_data['tiempo'][k] >= 600:
                idx.append(k)
    idx = list(set(idx))
    idx = sorted(idx)
    # contabilizar si el ratio de capital_perdedora/capital_ganadora es > 1.5
    r_cp_cg = []
    for f in range(len(idx)):
        for a in range(len(capital_perdedora)):
            if idx[f] == a:
                r_cp_cg.append(((capital_perdedora[a] / capital_ganadora[a])) * 100)
    idx_cp_cg = []  # idx de operaciones que capital_perdedora/capital_ganadora es > 1.5
    for h in range(len(r_cp_cg)):
        if r_cp_cg[h] > 1.5:
            idx_cp_cg.append(idx[h])
    idx_cap_g_tope = []  # indice de capital ganafora con que cerro opercion
    for i in range(len(i_cg)):
        if i < len(i_cg) - 1 and i_cg[i + 1] != i_cg[i] + 1:
            idx_cap_g_tope.append(i_cg[i])

    # -- -------------------------------------------------------------------------------- -- #
    # Cuantas veces paso que:
    # 1. Si cerraste una operacion ganadora y habia otra perdedora abierta que no cerraste en
    # ese momento
    v_op_A = len(idx)
    # 2. contabiliza las veces que: capital_perdedora/capital_acm <  capital_ganadora/capital_acm
    # para las perdedoras abiertas 
    count = 0
    for k in range(len(idx)):
        if df['capital_perdedora/capital_ganadora'][idx[k]] < \
                df['capital_ganadora/capital_acm'][idx[k]]:
            count = count + 1
    # 3. contabliza las veces que: capital_perdedora/capital_ganadora es > 1.5
    v_cp_15 = len(idx_cp_cg)

    if param_data.iloc[i_cg[0], -1] < param_data.iloc[i_cg[-1], -1] and \
            capital_ganadora[i_cg[0]] < capital_ganadora[i_cg[-1]] and \
            capital_perdedora[i_cp[0]] < capital_perdedora[i_cp[-1]] and \
            (capital_perdedora[i_cg[0]] / capital_ganadora[i_cg[0]]) * 100 > 1.5 \
            and (capital_perdedora[i_cg[-1]] / capital_ganadora[i_cg[-1]]) * 100 > 1.5:
        sens_de = True
    else:
        sens_de = False

    df_be_de = {'Ocurrencia': [v_op_A], 'Status_quo': [count / lose * 100],
                'Aversion_Perdida': [v_cp_15 / lose * 100],
                'Sensibilidad_Decreciente': [sens_de]}
    df_be_de = pd.DataFrame(df_be_de)

    return df_be_de