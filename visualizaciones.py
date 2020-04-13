# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: visualizaciones.py - visualizaciones generales para uso en el proyecto
# -- mantiene: Natasha Gamez
# -- repositorio: https://github.com/NatashaGamez/Lab_2_LNGO
# -- ------------------------------------------------------------------------------------ -- #
import plotly.graph_objects as go


def fig_ranking(ranking):
    """
    Parameters
    ----------
    :param param_data: DataFrame raking
    Returns
    -------
    :return: grafic

    """
    labels = ranking['Symbol']
    values = ranking['Rank %']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.15])])
    fig.update_layout(title_text='Ranking')
    return fig.show()


def fig_draw_down_up(df_profit_d, Est_MAD):
    """
    Parameters
    ----------
    :param param_data: DataFrame df_profit_d y Est_MAD
    Returns
    -------
    :return: grafic

    """
    x = df_profit_d['Timestamp']
    y = df_profit_d['Profit_acm_d']
    xd = Est_MAD['Valor'][3]
    xd = [xd[0], xd[1]]
    yd = []
    for j in range(df_profit_d.shape[0]):
        if df_profit_d['Timestamp'][j] == xd[0] or df_profit_d['Timestamp'][j] == xd[1]:
            yd.append(df_profit_d['Profit_acm_d'][j])

    xu = Est_MAD['Valor'][4]
    xu = [xu[0], xu[1]]
    yu = []
    for t in range(df_profit_d.shape[0]):
        if df_profit_d['Timestamp'][t] == xu[0] or df_profit_d['Timestamp'][t] == xu[1]:
            yu.append(df_profit_d['Profit_acm_d'][t])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, name="Profit_acm_d", line=dict(color='black')))
    fig.add_trace(go.Scatter(x=xd, y=yd, name="DrawDown", line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=xu, y=yu, name="DrawUp", line=dict(color='green', dash='dot')))
    fig.update_layout(title_text='DrawDown y DrawUp')

    return fig.show()


def fig_dispo_eff(df_be_de):
    """
    Parameters
    ----------
    :param param_data: DataFrame df_be_de
    Returns
    -------
    :return: grafic

    """
    y = [df_be_de['Status_quo'][0], df_be_de['Aversion_Perdida'][0]]
    x = ['Status_quo', 'Aversion_Perdida']
    fig = go.Figure(data=go.Bar(x=x, y=y))
    # Customize aspect
    fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=1.5, opacity=0.6)
    fig.update_layout(title_text='Disposition Effect')
    return fig.show()
