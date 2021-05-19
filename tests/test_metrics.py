import pytest, pandas as pd
from turingquant.metrics import *

def test_sharpe_ratio_should_return_float():
    returns = pd.Series([.1, .2, -.05])
    return isinstance(sharpe_ratio(returns), float)

def test_beta_should_return_float():
    returns = pd.Series([.1, .2, -.05])
    benchmark = pd.Series([-.15, .1, .05])
    return isinstance(beta(returns, benchmark), float)

def test_capm_should_return_float():
    returns = pd.Series([.1, .2, -.05])
    benchmark = pd.Series([-.15, .1, .05])
    return isinstance(capm(returns, benchmark, risk_free=0.3), float)