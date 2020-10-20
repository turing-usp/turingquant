"""Módulo para comparação e benchmarking de ativos e retornos."""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.ticker import PercentFormatter
from pandas_datareader import data


def benchmark(ticker, start: datetime, end: datetime, source='yahoo', plot=True):
    """
    Essa função fornece um plot de retorno acumulado de um ativo ao longo de um dado intervalo de tempo, definido pelos parâmetros start e end.
    Os dados são coletados da API do yahoo, caso haja dados faltantes, os retornos são contabilizados como nulos.

    Args:
        ticker (str): recebe o ticker do papel que será obtido.
        start (datetime): início do intervalo.
        end (datetime): final do intervalo.
        plot (bool): opcional; exibe o gráfico caso `True`.

    Returns:
        pd.series: uma série de ativos indexados com o tempo com o retorno cumulativo para o período.

    """

    asset = data.DataReader(ticker, data_source=source, start=start, end=end)
    returns_daily = asset['Close'].pct_change().fillna(0)
    cumulative = pd.DataFrame.cumprod(1 + returns_daily) - 1
    if plot:
        cumulative.plot()
    return cumulative


def benchmark_ibov(start: datetime, end: datetime, source='yahoo', plot=True):
    """
    Essa função produz um plot da evolução do Índice Bovespa ao longo de um dado intervalo, definido pelos parâmetros start e end.

    Args:
        start (datetime): início do intervalo.
        end (datetime): final do intervalo.
        plot (bool): opcional; exibe o gráfico caso `True`.

    Returns:
        pd.series: uma série temporal com o retorno acumulado do Ibovespa para o período.
    """

    return benchmark('^BVSP', start=start, end=end, source=source, plot=plot)


def benchmark_sp500(start: datetime, end: datetime, source='yahoo', plot=True):
    """
    Essa função produz um plot da evolução do Índice S&P500 ao longo de um dado intervalo, definido pelos parâmetros start e end.

    Args:
        start (datetime): início do intervalo.
        end (datetime): final do intervalo.
        plot (bool): opcional; exibe o gráfico caso `True`.

    Returns:
        pd.series: uma série temporal com o retorno acumulado do S&P500 para o período.
    """

    return benchmark('^GSPC', start=start, end=end, source=source, plot=plot)
