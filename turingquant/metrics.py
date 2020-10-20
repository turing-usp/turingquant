"""Módulo para metrificação de ativos e retornos."""

import numpy as np
import pandas as pd
import plotly.express as px


def sharpe_ratio(returns, risk_free=0):
    """
    Essa função, a partir da definição do parâmetro de retorno, fornece o sharpe ratio do ativo, com base na média histórica e desvio padrão dos retornos.
    O risk free considerado é nulo.

    Args:
        returns (pd.series): série com o retorno do ativo.
        risk_free (float): risk free utilizado para cálculo do sharpe ratio.

    Returns:
        float: índice de sharpe do ativo.
    """

    expected_returns = returns.mean()
    risk = returns.std()

    return(expected_returns - risk_free) / risk


def beta(returns, benchmark):
    """
    Essa função, a partir do fornecimento dos retornos do ativo e do benchmark, calcula o beta do ativo.

    Args:
        returns (pd.series): série com o retorno do ativo.
        benchmark (pd.series): série com o retorno do benchmark.

    Returns:
        float: Beta do ativo
    """
    concat = np.matrix([returns, benchmark])
    cov = np.cov(concat)[0][1]
    benchmark_vol = np.var(benchmark)

    return cov / benchmark_vol


def alpha(start_price, end_price, dps):
    """
    Essa função, com o fornecimento do preço final, dos dividendos por ação e do preço inicial, a calcula o alfa de um ativo.

    Args:
        start_price (float): preço inicial.
        end_price (float): preço final.
        dps(float): dividendos por ação.

    Returns:
        float: alpha do ativo
    """

    return(end_price + dps - start_price) / start_price


def drawdown(return_series, plot=True):
    """
    Calcula e plota o drawdown percentual para uma série de retornos.

    Args:
        return_series (pd.Series): série de retornos para o qual será calculado o Drawdown.
        plot (bool): se `True`, plota um gráfico de linha com o Drawdown ao longo do tempo.

    Returns:
        pd.Series: uma série com os valores percentuais do Drawdown.
    """

    wealth_index = 1000 * (1 + return_series).cumprod()
    previous_peaks = wealth_index.cummax()
    drawdowns = pd.Series((wealth_index - previous_peaks) /
                          previous_peaks, name='Drawdown')

    if plot:
        fig = px.line(drawdowns, x=drawdowns.index,
                      y='Drawdown', title='Drawdown')
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='Drawdown (%)')
        fig.show()

    return drawdowns


def rolling_beta(returns, benchmark, window=60, plot=True):
    """
    Plota o beta móvel para um ativo e um benchmark de referência, na forma de séries de retornos.

    Args:
        returns (array): série de retornos para o qual o beta será calculado.
        benchmark (array): série de retornos para usar de referência no cálculo do beta.
        window (int): janela móvel para calcular o beta ao longo do tempo.
        plot (bool): se `True`, plota um gráfico de linha com o beta ao longo do tempo.

    Returns:
        pd.Series: uma série com os valores do Beta para os últimos `window` dias.
        A série não possui os `window` primeiros dias.

    """
    rolling_beta = pd.Series([beta(returns[i-window:i], benchmark[i-window:i])
                              for i in range(window, len(returns))], index=returns[window:].index)
    if plot:
        fig = px.line(rolling_beta, title="Beta móvel")
        overall_beta = beta(returns, benchmark)
        fig.update_layout(shapes=[
            dict(
                type='line',
                xref='paper', x0=0, x1=1,
                yref='y', y0=overall_beta, y1=overall_beta,
                line=dict(
                    color='grey',
                    width=2,
                    dash='dash'
                )
            )
        ], annotations=[
            dict(
                text='beta total: %.3f' % overall_beta,
                xref='paper', x=0.05,
                yref='y', y=overall_beta,
                xanchor='left'
            )
        ])
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='Beta móvel: ' + str(window) + ' períodos')
        fig.show()
    return rolling_beta


def rolling_sharpe(returns, window, risk_free=0, plot=True):
    """
    Plota o sharpe móvel para um ativo e um benchmark de referência, na forma de séries de retornos.

    Args:
        returns (array): série de retornos para o qual o Sharpe Ratio será calculado.
        window (int): janela móvel para calcular o Sharpe ao longo do tempo.
        risk_free (float): valor da taxa livre de risco para cálculo do Sharpe.
        plot (bool): se `True`, plota um gráfico de linha com o Sharpe ao longo do tempo.

    Returns:
        pd.Series: uma série com os valores do Sharpe para os últimos `window` dias.
        A série não possui os `window` primeiros dias.

    """
    rolling_sharpe = pd.Series([sharpe_ratio(returns[i - window:i], risk_free)
                                for i in range(window, len(returns))], returns[window:].index)
    if plot:
        fig = px.line(rolling_sharpe, title="Sharpe móvel")
        overall_sharpe = sharpe_ratio(returns, risk_free)
        fig.update_layout(shapes=[
            dict(
                type='line',
                xref='paper', x0=0, x1=1,
                yref='y', y0=overall_sharpe, y1=overall_sharpe,
                line=dict(
                    color='grey',
                    width=2,
                    dash='dash'
                )
            )
        ], annotations=[
            dict(
                text='sharpe total: %.3f' % overall_sharpe,
                xref='paper', x=0.05,
                yref='y', y=overall_sharpe,
                xanchor='left'
            )
        ])
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='Sharpe móvel: ' +
                         str(window) + ' períodos')
        fig.show()
    return rolling_sharpe


def ewma_volatility(close_prices, return_type, window, plot=True):
    """
    Essa função possibilita a visualização da volatilidade a partir do cálculo da EWMA e da plotagem do gráfico 
    dessa métrica ao longo de um período.

    Parâmetros:
        close_prices (pd.DataFrame): série de preços de fechamento que será utilizado de base para o cálculo da EWMA;
        return_type (string): tipo de retorno (simple - 'simp' ou logarítmico - 'log') que será utilizado de base para cálculo;
        window (int): janela móvel para cálculo da EWMA;
        plot (bool): se True, plota o gráfico de linha da EWMA ao longo do tempo

    Retorna:
        ewma_volatility (pd.DataFrame): um dataframe indexado à data com os valores de EWMA dos últimos window dias
    """
    if return_type == 'log':
        returns = np.log(close_prices/close_prices.shift(1))
    elif return_type == 'simp':
        returns = close_prices.pct_change()
    else:
        raise ValueError("Tipo de retorno inválido")
    ewma_volatility = returns.ewm(span=window).std()
    ewma_volatility = pd.Series.to_frame(ewma_volatility)
    if plot:
        fig = px.line(ewma_volatility, x=ewma_volatility.index,
                      y='Close', title='EWMA')
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='EWMA')
        fig.show()
        return ewma_volatility
    if plot == False:
        return ewma_volatility


def garman_klass_volatility(high_prices, low_prices, close_prices, open_prices, window, time_scale=1, plot=True):
    """
    Estima a volatilidade a partir dos seguintes preços: alta, baixa, abertura e fechamento

    Parâmetros:
        high_prices (pd.DataFrame): série de preços de alta de uma ação
        low_prices (pd.DataFrame): série de preços de baixa de uma ação
        close_prices (pd.DataFrame): série de preços de fechamento de uma ação
        open_prices (pd.DataFrame): série de preços de abertura de uma ação
        window (int): janela das estimativa de volatilidade
        time_scale (int): fator de escala da volatilidade, por padrão é 1 (diária)
        plot (bool): se 'True', plota um gráfico da volatilidade móvel

    Retorna: 
        garman_klass_vol (pd.Series): série das estimativas de volatildade
    """
    # Calculando parcelas internas da somatoria
    high_low_ratio = (1 / 2) * \
        (np.log(np.divide(high_prices, low_prices))) ** 2

    close_open_ratio = -(2 * np.log(2) - 1) * (
        np.log(np.divide(close_prices, open_prices)) ** 2
    )

    # Somando parcelas calculadas
    log_ratio = high_low_ratio + close_open_ratio.values

    # Criando dataframe para atribuir as volatilidades
    garman_klass_vol = pd.Series(log_ratio, name='Garman Klass', copy=True)

    # Termo constante fora da somatoria (Considerando vol diaria)
    Period_const = time_scale / window

    # Atribuindo not a number, para os valores iniciais
    garman_klass_vol.iloc[:window] = np.nan

    # iteração do centro de massa da vol
    for date in range(window, len(high_prices)):
        garman_klass_vol.iloc[date] = np.sqrt(
            Period_const * np.sum(log_ratio.iloc[date - window: date])
        )

    if plot:
        fig = px.line(garman_klass_vol, title='Garman Klass')
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='Volatilidade')

        mean_garman_klass = garman_klass_vol.mean()
        fig.update_layout(shapes=[
            dict(
                type='line',
                xref='paper', x0=0, x1=1,
                yref='y', y0=mean_garman_klass, y1=mean_garman_klass,
                line=dict(
                    color='grey',
                    width=2,
                    dash='dash'
                )
            )
        ], annotations=[
            dict(
                text='Volatilidade média: %.3f' % mean_garman_klass,
                xref='paper', x=0.95,
                yref='y', y=1.1 * mean_garman_klass,
                xanchor='left'
            )
        ])

        fig.show()

    return garman_klass_vol


def parkinson_volatility(high_prices, low_prices, window, time_scale=1, plot=True):
    """
    Estimando a volatilidade a partir dos preços de Alta e de Baixa

    Parâmetros:
        high (pd.DataFrame): série de preços de alta de uma ação
        low (pd.DataFrame): série de preços de baixa de uma ação
        window (int): janela das estimativa de volatilidade
        time_scale (int): fator de escala da volatilidade, por padrão é 1 (diária)
        plot (bool): se 'True', plota um gráfico da volatilidade móvel

    Retorna: 
        garman_klass_vol (pd.Series): série das estimativas de volatildade

    """

    log_ratio = np.log(np.divide(high_prices, low_prices)) ** 2

    parkinson_vol = pd.Series(log_ratio, name='Parkinson', copy=True)

    Period_const = time_scale / (4 * window * np.log(2))

    parkinson_vol.iloc[:window] = np.nan

    for date in range(window, len(high_prices)):
        parkinson_vol.iloc[date] = np.sqrt(
            Period_const * np.sum(log_ratio.iloc[date - window: date])
        )

    if plot:
        fig = px.line(parkinson_vol, title='Número de Parkinson')
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='Volatilidade')

        mean_parkinson = parkinson_vol.mean()
        fig.update_layout(shapes=[
            dict(
                type='line',
                xref='paper', x0=0, x1=1,
                yref='y', y0=mean_parkinson, y1=mean_parkinson,
                line=dict(
                    color='grey',
                    width=2,
                    dash='dash'
                )
            )
        ], annotations=[
            dict(
                text='Volatilidade média: %.3f' % mean_parkinson,
                xref='paper', x=0.95,
                yref='y', y=1.1 * mean_parkinson,
                xanchor='left'
            )
        ])
        fig.show()

    return parkinson_vol


def rolling_std(close_prices, return_type, window, plot=True):
    """
    Essa função possibilita a visualização da volatilidade a partir do cálculo da desvio padrão móvel e da plotagem do gráfico dessa
    métrica ao longo de um período.  

    Parâmetros:
        close_prices (pd.DataFrame): série de preços de fechamento que será utilizado de base para o cálculo do desvio padrão móvel;
        return_type (string): tipo de retorno (simple - 'simp' ou logarítmico - 'log') que será utilizado de base para cálculo;
        window (int): janela móvel para cálculo do desvio padrão móvel;
        plot (bool): se True, plota o gráfico de linha do desvio padrão móvel ao longo do tempo

    Retorna:
        rolling_std (pd.DataFrame): um dataframe indexado à data com os valores de desvio padrão móvel dos últimos window dias
    """
    if return_type == 'log':
        returns = np.log(close_prices/close_prices.shift(1))
    elif return_type == 'simp':
        returns = close_prices.pct_change()
    else:
        raise ValueError("Tipo de retorno inválido")
    rolling_std = returns.rolling(window).std()
    rolling_std = pd.Series.to_frame(rolling_std)
    if plot:
        fig = px.line(rolling_std, x=rolling_std.index,
                      y='Close', title='Desvio Padrão Móvel')
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='Desvio padrão móvel')
        fig.show()
        return rolling_std
    if plot == False:
        return rolling_std
