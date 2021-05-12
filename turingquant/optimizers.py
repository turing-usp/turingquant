'''Módulo para otimização de portfólios.'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Markowitz:
    '''
    Otimizador baseado na Teoria Moderna do Portfólio, de Harry Markowitz.
    A partir dos dados de fechamento, gera portfólios com pesos aleatórios e calcula
    os melhores pesos utilizando o risco e retorno da carteira. 
    
    Parâmetros:
        df_close (pd.DataFrame): DataFrame com os preços de fechamento dos ativos
        num_portfolios (int): números de portfólios gerados 
        risk_free (float): taxa de risco livre utilizada para cálculo do sharpe ratio.
    
    Atributos:
        wallets (dict): dicionário contendo os valores 'weights', 'returns', 'vol' e 'sharpe_ratio'
                        de todos os portfólios gerados 
    
    '''
    def __init__(self, df_close, num_portfolios = 10000, risk_free = 0):
        self.df = df_close
        self.num_portfolios = num_portfolios
        self.risk_free = risk_free
        self.wallets = self._generate_wallets()
    
    def _generate_wallets(self):
        '''
        Gera carteiras com pesos aleatórios.

        Returns:
            wallets (dict): dicionário contendo os valores 'weights', 'returns', 'vol' e 'sharpe_ratio'
                            de todos os portfólios gerados 
        '''
        # vetores de dados
        portfolio_weights = []
        portfolio_exp_returns = []
        portfolio_vol = []
        portfolio_sharpe = []
        
        # retorno simples 
        r = self.df.pct_change()
        mean_returns = r.mean() * 252
        
        # matriz de covariância 
        covariance = np.cov(r[1:].T)

        for i in range(self.num_portfolios):
            # gerando pesos aleatórios
            k = np.random.rand(len(self.df.columns))
            w = k / sum (k)

            # retorno
            R = np.dot(mean_returns, w)

            # risco
            vol = np.sqrt(np.dot(w.T, np.dot(covariance, w))) * np.sqrt(252)

            # sharpe ratio
            sharpe = (R - self.risk_free)/vol

            portfolio_weights.append(w)
            portfolio_exp_returns.append(R)
            portfolio_vol.append(vol)
            portfolio_sharpe.append(sharpe)

        wallets = {'weights': portfolio_weights,
                  'returns': portfolio_exp_returns,
                  'vol':portfolio_vol,
                  'sharpe': portfolio_sharpe}
    
        return wallets
        
    def plot_efficient_frontier(self, method = 'sharpe_ratio'):
        '''
        Plota gráfico com a fronteira eficiente dos portfólios gerados. 
        
        Args: 
            method (string): Método utilizado para indicar o melhor portfólio
                            'sharpe_ratio' - Portfólio com melhor Sharpe ratio
                            'volatility' - Portfólio com menor volatilidade
                            'return' - Portfólio com maior retorno
        
        '''
        vol = self.wallets['vol']
        returns = self.wallets['returns']
        sharpe = self.wallets['sharpe']
        
        if method == 'sharpe_ratio':
            
            indice = np.array(sharpe).argmax()
            y_axis = returns[indice]
            X_axis = vol[indice]

        elif method == 'volatility':
            
            indice = np.array(vol).argmin()
            y_axis = returns[indice]
            X_axis = vol[indice]

        elif method == 'return': 
            
            indice = np.array(returns).argmax()
            y_axis = returns[indice]
            X_axis = vol[indice]

        plt.scatter(vol, returns, c = sharpe, cmap = 'viridis')
        plt.scatter(X_axis, y_axis, c = 'red', s = 50)
        plt.colorbar(label = 'Sharpe Ratio')
        plt.title("Efficient Frontier")
        plt.xlabel("Volatility")
        plt.ylabel("Expected return")
        plt.show()

    def best_portfolio(self, method = 'sharpe_ratio'):
        '''
        Retorna os pesos do melhor portfólio de acordo com o método escolhido.
        
        Args:
            method (string): Método utilizado para indicar o melhor portfólio
                            'sharpe_ratio' - Portfólio com melhor Sharpe ratio
                            'volatility' - Portfólio com menor volatilidade
                            'return' - Portfólio com maior retorno
        Returns: 
            weights (np.array): Numpy array contendo os pesos do melhor portfólio. 
        
        '''
        
        vol = self.wallets['vol']
        returns = self.wallets['returns']
        sharpe = self.wallets['sharpe']
        weights = self.wallets['weights']
        
        if method == 'sharpe_ratio':

            indice = np.array(sharpe).argmax()

        elif method == 'volatility':

            indice = np.array(vol).argmin()

        elif method == 'return':

            indice = np.array(returns).argmax()

        return weights[indice]
    