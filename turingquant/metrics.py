"""Módulo para metrificação de ativos e retornos."""

import numpy as np
import pandas as pd
from scipy import stats

def sharpe_ratio(returns, risk_free=0, time_scale=252):
    """
    Essa função, a partir da definição do parâmetro de retorno, fornece o sharpe ratio do ativo, com base na média histórica e desvio padrão dos retornos.
    O risk free considerado é nulo.

    Args:
        returns (pd.series): série com o retorno do ativo.
        risk_free (float): risk free utilizado para cálculo do sharpe ratio.
        time_scale (int): fator de escala do sharpe ratio, que é o número de amostras em um ano. Caso fosse uma série temporal diária: 252; série temporal mensal: 12

    Returns:
        float: índice de sharpe do ativo.
    """

    expected_returns = np.mean(returns)
    risk = np.std(returns)

    sharpe = (expected_returns * time_scale - risk_free) / (risk * np.sqrt(time_scale))

    return sharpe


def beta(returns, benchmark):
    """
    Essa função, a partir do fornecimento dos retornos do ativo e do benchmark, calcula o beta do ativo.

    Args:
        returns (pd.Series): série com o retorno do ativo.
        benchmark (pd.Series): série com o retorno do benchmark.

    Returns:
        float: Beta do ativo
    """

    assert returns.shape[0] == benchmark.shape[0], "Séries temporais com dimensões diferentes"

    cov = np.cov(returns, benchmark)[0][1]

    benchmark_vol = np.var(benchmark)

    return cov / benchmark_vol

def capm(returns, market_returns, risk_free):
    """
    Essa função, com o fornecimento dos retornos de um portfólio ou ativo, dos retornos do mercado e da retorno sem risco, 
    calcula o retorno esperado pela abordagem CAPM. Essa abordagem considera o mercado (benchmark) e as relações com os ativos 
    como parâmetro para estimar o retorno esperado.

    Args:
        returns (pd.Series ou np.array): vetor de retornos
        market_returns (pd.Series ou np.array): vetor de retornos do mercado ou benchmark
        risk_free (float): retorno livre de risco
        
    Returns:
        float: retorno esperado pela abordagem CAPM
    """
    beta = beta(returns, market_returns)
    expected_market_returns = market_returns.mean()
    expected_returns = risk_free + beta * (expected_market_returns - risk_free)
    return expected_returns


def alpha(start_price, end_price, dividends):
    """
    Essa função, com o fornecimento do preço final, dos dividendos por ação e do preço inicial, a calcula o alfa de um ativo.

    Args:
        start_price (float): preço inicial.
        end_price (float): preço final.
        dividends (float): dividendos por ação.

    Returns:
        float: alpha do ativo
    """

    return (end_price + dividends - start_price) / start_price


def drawdown(returns):
    """
    Calcula o drawdown percentual para uma série de retornos.

    Args:
        returns (pd.Series): série de retornos para a qual será calculado o drawdown.
    
    Returns:
        pd.Series: uma série com os valores percentuais do Drawdown.
    """

    cum_returns = (1 + returns).cumprod()
    peeks = cum_returns.cummax()
    drawdowns = pd.Series((cum_returns/peeks - 1)*100,
                          name='Drawdown')
    return drawdowns

def rolling_beta(returns, benchmark, window=60):
    """
    Calcula o beta móvel para um ativo e um benchmark de referência, na forma de séries de retornos.

    Args:
        returns (array): série de retornos para o qual o beta será calculado.
        benchmark (array): série de retornos para usar de referência no cálculo do beta.
        window (int): janela móvel para calcular o beta ao longo do tempo.

    Returns:
        pd.Series: uma série com os valores do Beta para os últimos `window` dias.
        A série não possui os `window` primeiros dias.

    """
    rolling_beta = pd.Series([beta(returns[i-window:i], benchmark[i-window:i])
                              for i in range(window, len(returns))], index=returns[window:].index)
    return rolling_beta

def rolling_sharpe(returns, window, risk_free=0):
    """
    Calcula o sharpe móvel para um ativo e um benchmark de referência, na forma de séries de retornos.

    Args:
        returns (pd.Series): série de retornos para o qual o Sharpe Ratio será calculado.
        window (int): janela móvel para calcular o Sharpe ao longo do tempo.
        risk_free (float): valor da taxa livre de risco para cálculo do Sharpe.

    Returns:
        pd.Series: uma série com os valores do Sharpe para os últimos `window` dias.
        A série não possui os `window` primeiros dias.

    """
    rolling_sharpe = pd.Series([sharpe_ratio(returns[i - window:i], risk_free)
                                for i in range(window, len(returns))], returns[window:].index)
    return rolling_sharpe

def ewma_volatility(returns, window):
    """
    Essa função calcula a volatilidade por EWMA ao longo de um período.

    Args:
        returns (pd.Series): série de retornos para o qual o EWMA será calculado.
        window (int): janela móvel para cálculo da EWMA;

    Returns:
        pd.Series: uma série com os valores de EWMA dos últimos `window` dias
    """

    ewma_volatility = returns.ewm(span=window).std()
    
    return ewma_volatility


def garman_klass_volatility(high_prices, low_prices, close_prices, open_prices, window, time_scale=1):
    """
    Estima a volatilidade a partir dos seguintes preços: alta, baixa, abertura e fechamento

    Args:
        high_prices (pd.DataFrame): série de preços de alta de uma ação
        low_prices (pd.DataFrame): série de preços de baixa de uma ação
        close_prices (pd.DataFrame): série de preços de fechamento de uma ação
        open_prices (pd.DataFrame): série de preços de abertura de uma ação
        window (int): janela das estimativa de volatilidade
        time_scale (int): fator de escala da volatilidade, por padrão é 1 (diária)

    Returns: 
        pd.Series: série das estimativas de volatildade
    """

    high_low_ratio = (1 / 2) * \
        (np.log(np.divide(high_prices, low_prices))) ** 2

    close_open_ratio = -(2 * np.log(2) - 1) * (
        np.log(np.divide(close_prices, open_prices)) ** 2
    )

    log_ratio = high_low_ratio + close_open_ratio.values

    garman_klass_vol = pd.Series(log_ratio, name='Garman Klass', copy=True)

    Period_const = time_scale / window

    garman_klass_vol.iloc[:window] = np.nan

    for date in range(window, len(high_prices)):
        garman_klass_vol.iloc[date] = np.sqrt(
            Period_const * np.sum(log_ratio.iloc[date - window: date])
        )

    return garman_klass_vol


def parkinson_volatility(high_prices, low_prices, window, time_scale=1, plot=False):
    """
    Estimando a volatilidade a partir dos preços de Alta e de Baixa

    Args:
        high (pd.DataFrame): série de preços de alta de uma ação
        low (pd.DataFrame): série de preços de baixa de uma ação
        window (int): janela das estimativa de volatilidade
        time_scale (int): fator de escala da volatilidade, por padrão é 1 (diária)

    Returns: 
        pd.Series: série das estimativas de volatildade

    """

    log_ratio = np.log(np.divide(high_prices, low_prices)) ** 2

    parkinson_vol = pd.Series(log_ratio, name='Parkinson', copy=True)

    Period_const = time_scale / (4 * window * np.log(2))

    parkinson_vol.iloc[:window] = np.nan

    for date in range(window, len(high_prices)):
        parkinson_vol.iloc[date] = np.sqrt(
            Period_const * np.sum(log_ratio.iloc[date - window: date])
        )

    return parkinson_vol


def rolling_std(returns, window):
    """
    Essa função calcula volatilidade a partir do cálculo da desvio padrão móvel.

    Args:
        returns (pd.Series): série de retornos para o qual o desvio padrão será calculado.
        window (int): janela móvel para cálculo do desvio padrão móvel;

    Returns:
        pd.Series: uma série indexado à data com os valores de desvio padrão móvel dos últimos window dias
    """

    rolling_std = returns.rolling(window).std()

    return rolling_std


def returns(close_prices, return_type='simple'):
    """
    Essa função permite o cálculo rápido do retorno de uma ação ao longo do tempo.

    Args:
        close_prices (pd.Series): série de preços de fechamento que será utilizada de base para o cálculo do retorno;
        return_type (string): tipo de retorno (simples - 'simple' ou logarítmico - 'log') a ser calculado;

    Returns:
        pd.Series: série com os valores do retorno ao longo do tempo
    """
    if return_type == "simple":
        returns = close_prices.pct_change()
    elif return_type == "log":
        returns = np.log(close_prices/close_prices.shift(1))
    else:
        raise ValueError("Tipo de retorno inválido")

    return returns

def cumulative_returns(returns, return_type):
    """
    Essa função permite o cálculo do retorno cumulativo ao longo do tempo.

    Args:
        returns (pd.Series): série de retornos da ação ao longo do tempo;
        return_type (string): tipo de retorno (simples - 'simp' ou logarítmico - 'log') presente na série.

    Returns:
        pd.Series: série com os valores de retorno cumulativo ao longo do tempo
    """
    if return_type == "log":
        cumulative_returns = returns.cumsum()
    elif return_type == "simp":
        cumulative_returns = (returns + 1).cumprod() - 1
    else:
        raise ValueError("Tipo de retorno inválido")

    return cumulative_returns

def cagr(returns, time_scale=252):
    """
    Calcula o CAGR que é a taxa composta de crescimento anual.
    Args:
        returns (pd.Series): série de retornos para a qual será calculado o drawdown.
        time_scale (int): fator de escala do cagr, que é o número de amostras em um ano. Caso fosse uma série temporal diária: 252; série temporal mensal: 12
    Returns:
        float: cagr do ativo.
    """

    cumulative_return = (1 + returns).cumprod()[-1]

    return (cumulative_return ** (1/(returns.shape[-1] / time_scale)) - 1)


def mar_ratio(returns, time_window, time_scale=252):
    """
    Calcula e plota o drawdown percentual para uma série de retornos.
    Args:
        returns (pd.Series): série de retornos para a qual será calculado o mar ratio.
        time_window (float): janela de tempo que o mar ratio será calculado em relação a escala de tempo. time_window = 3 e time_scale = 252 denota uma janela de 3 anos (Calmar Ratio).
        time_scale (int): fator de escala do mar ratio, que é o número de amostras em um ano. Caso fosse uma série temporal diária: 252; série temporal mensal: 12
    Returns:
        float: valor do mar ratio do ativo
    """

    returns_window = returns[-time_window * time_scale:]

    drawdowns = drawdown(returns_window)
    max_drawdown = abs(drawdowns).max()

    mar_ratio = returns_window.mean() * time_scale / max_drawdown

    return mar_ratio

def value_at_risk(returns, confidance_level = 0.95, window = 1, method = 'variance-covariance'):
    
    if method == 'variance-covariance':
        mean = np.mean(returns)
        
        std = np.std(returns)
        
        var = stats.norm.ppf(1 - confidance_level, mean, std)
        
    elif method == 'historical':
        returns = returns.sort_values(ascending = True)
        
        var = returns.quantile(1 - confidance_level)
    
    if window != 1:
        var = var * np.sqrt(window)
    
    return var
    