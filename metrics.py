import numpy as np


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


def beta(returns, benchmark):
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
