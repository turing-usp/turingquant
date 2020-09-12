import numpy as np
import pandas as pd
import plotly.express as px


def sharpe_ratio(returns, risk_free=0):
    """
    Essa função, a partir da definição do parâmetro de retorno, fornece o sharpe ratio do ativo, com base na média histórica e desvio padrão dos retornos.
    O risk free considerado é nulo.

    returns [pd.series]: série com o retorno do ativo

    risk_free [float]: risk free utilizado para cálculo do sharpe ratio.
    """

    expected_returns = returns.mean()
    risk = returns.std()

    return(expected_returns - risk_free) / risk


def beta(returns, benchmark, rolling_window=None, plot=False):
    """
    Essa função, a partir do fornecimento dos retornos do ativo e do benchmark, calcula o beta do ativo.

    returns [pd.series]: série com o retorno do ativo

    benchmark [pd.series]: série com o retorno do benchmark
    """
    concat = np.matrix([returns, benchmark])
    cov = np.cov(concat)[0][1]
    benchmark_vol = np.std(benchmark)

    return cov / benchmark_vol


def alpha(end_price, dps, start_price):
    """
    Essa função, com o fornecimento do preço final, dos dividendos por ação e do preço inicial, a calcula o alfa de um ativo.

    end_price [float]:

    dps[float]:

    start_proce[float]:
    """

    return(end_price + dps - start_price) / start_price


def rolling_beta(returns, benchmark, window, plot=True):
    """
    Plota o beta móvel para um ativo e um benchmark de referência, na forma de séries de retornos.

    Parâmetros:
        returns (array): série de retornos para o qual o beta será calculado.
        benchmark (array): série de retornos para usar de referência no cálculo do beta.
        window (int): janela móvel para calcular o beta ao longo do tempo.
        plot (bool): se `True`, plota um gráfico de linha com o beta ao longo do tempo.

    Retorna:
        rolling_beta (pd.Series): uma série com os valores do Beta para os últimos `window` dias.
            A série não possui os `window` primeiros dias.

    """
    returns = pd.DataFrame(returns)
    benchmark = pd.DataFrame(benchmark)
    merged = returns.merge(benchmark, left_index=True, right_index=True)
    rolling_beta = merged.iloc[:, 0].rolling(window).cov(merged.iloc[:, 1])/merged.iloc[:, 1].rolling(window).var()
    rolling_beta = rolling_beta[window:]
    rolling_beta.name = 'beta'
    if plot:
        fig = px.line(rolling_beta, title="Beta móvel")
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title_text='Tempo')
        fig.update_yaxes(title_text='Beta móvel: ' + str(window) + ' dias')
        fig.show()
    return rolling_beta


def test_metrics():
    """
    Essa função define uma série aleatória de 50 elementos de retornos de um ativo fictício e de um índice de mercado e, a partir deles,
    fornece o beta e o sharpe ratio do ativo fictício, com o objetivo de testar as funções beta e sharpe_ratio.
    """

    returns = np.random.uniform(-1, 1, 50)
    market = np.random.uniform(-1, 1, 50)

    start

    print("Sharpe: ", sharpe_ratio(returns))
    print("Beta: ", beta(returns, market))
