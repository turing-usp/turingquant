#%%
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pandas_datareader import data

def benchmark(ticker, start: pd.datetime, end: pd.datetime, source='yahoo', plot=True):
    asset = data.DataReader(ticker, data_source=source, start=start, end=end)
    returns_daily = asset['Close'].pct_change().fillna(0)
    cumulative = pd.DataFrame.cumprod(1+returns_daily) - 1
    if plot:
        cumulative.plot()
    return cumulative

def benchmark_ibov(start: pd.datetime, end: pd.datetime, source='yahoo', plot=True):
    return benchmark('^BVSP', start=start, end=end, source=source, plot=plot)

def benchmark_sp500(start: pd.datetime, end: pd.datetime, source='yahoo', plot=True):
    return benchmark('^GSPC', start=start, end=end, source=source, plot=plot)