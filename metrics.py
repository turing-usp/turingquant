import numpy as np


def sharpe_ratio(returns, risk_free=0):
    expected_returns = returns.mean()
    risk = returns.std()

    return(expected_returns - risk_free) / risk


def beta(returns, benchmark):
    concat = np.matrix([returns, benchmark])
    cov = np.cov(concat)[0][1]
    benchmark_vol = np.std(benchmark)

    return cov / benchmark_vol


def alpha(end_price, dps, start_price):

    return(end_price + dps - start_price) / start_price


def test_metrics():
    returns = np.random.uniform(-1, 1, 50)
    market = np.random.uniform(-1, 1, 50)

    start

    print("Sharpe: ", sharpe_ratio(returns))
    print("Beta: ", beta(returns, market))
