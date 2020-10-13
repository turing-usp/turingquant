import pandas as pd
import plotly.express as px
from datetime import datetime
from pandas_datareader import data


def benchmark(ticker, start: datetime, end: datetime, source='yahoo', plot=True):
    """
    Essa função fornece um plot de retorno acumulado de um ativo ao longo de um dado intervalo de tempo, definido pelos parâmetros start e end.
    Os dados são coletados da API do yahoo, caso haja dados faltantes, os retornos são contabilizados como nulos.

    ticker[str]: recebe o ticker do papel que será obtido

    start[datetime]: início do intervalo

    end[datetime]: final do interval

    plot[bool]: (default = True) se True, realiza o plot
    """

    asset = data.DataReader(ticker, data_source=source, start=start, end=end)
    asset['Returns'] = asset['Close'].pct_change().fillna(0)
    asset['Cumulative Returns'] = pd.DataFrame.cumprod(1 + asset['Returns']) - 1

    if plot:
        fig = px.line(asset, x=asset.index, y='Cumulative Returns', title='Retorno cumulativo ' + ticker)
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='Retorno cumulativo')
        fig.show()

    return asset['Cumulative Returns']


def benchmark_ibov(start: datetime, end: datetime, source='yahoo', plot=True):
    """
    Essa função produz um plot da evolução do Índice Bovespa ao longo de um dado intervalo, definido pelos parâmetros start e end.

    start[datetime]: início do intervalo

    end[datetime]: final do interval

    plot[bool]: (default = True) se True, realiza o plot
    """

    return benchmark('^BVSP', start=start, end=end, source=source, plot=plot)


def benchmark_sp500(start: datetime, end: datetime, source='yahoo', plot=True):
    """
    Essa função produz um plot da evolução do Índice S&P500 ao longo de um dado intervalo, definido pelos parâmetros start e end.

    start[datetime]: início do intervalo

    end[datetime]: final do interval

    plot[bool]: (default = True) se True, realiza o plot
    """

    return benchmark('^GSPC', start=start, end=end, source=source, plot=plot)
