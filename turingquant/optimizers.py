'''Módulo para otimização de portfólios.'''

import pandas as pd
import numpy as np
import plotly.express as px


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
        wallets (pd.DataFrame): DataFrame contendo os valores 'weights', 'returns', 'vol' e 'sharpe_ratio'
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

        # métricas (colunas) de cada portfólio (linhas)
        metrics = pd.DataFrame({
            'returns': portfolio_exp_returns,
            'vol': portfolio_vol,
            'sharpe': portfolio_sharpe
        })

        # pesos de cada ativo (colunas) por portfólio (linhas)        
        weights = pd.DataFrame(portfolio_weights, columns=self.df.columns)

        # carteira = métricas + colunas com o peso de cada ativo
        wallets = pd.concat([metrics, weights], axis=1)
    
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
            best_port_idx = np.array(sharpe).argmax()

        elif method == 'volatility':            
            best_port_idx = np.array(vol).argmin()

        elif method == 'return':             
            best_port_idx = np.array(returns).argmax()

        else:
            raise ValueError(
                f"method espera 'sharpe_ratio', 'volatility' ou 'return', não '{method}'"
            )

        y_axis = returns[best_port_idx]
        X_axis = vol[best_port_idx]

        # Plota todos os portfólios
        fig = px.scatter(
            self.wallets,
            x='vol',
            y='returns',
            hover_data=self.df.columns,
            color='sharpe'
        )

        # Customizações gerais do gráfico
        fig.update_layout(
            width=600, height=600,
            margin=dict(l=10, r=10, t=50, b=10),
            title='Efficient Frontier',
            xaxis_title="Volatility",
            yaxis_title="Returns",
        )

        # Exibe o ponto do melhor portfólio em vermelho
        fig.update_traces(
            marker=dict(size=9, opacity=0.6),
            selectedpoints=[best_port_idx],
            selected=dict(marker=dict(color='red', opacity=1))
        )

        fig.show()

    def best_portfolio(self, method = 'sharpe_ratio'):
        '''
        Retorna os pesos do melhor portfólio de acordo com o método escolhido.
        
        Args:
            method (string): Método utilizado para indicar o melhor portfólio
                            'sharpe_ratio' - Portfólio com melhor Sharpe ratio
                            'volatility' - Portfólio com menor volatilidade
                            'return' - Portfólio com maior retorno
        Returns: 
            weights (pd.Series): Pandas Series contendo os pesos do melhor portfólio.
        '''
        
        vol = self.wallets['vol']
        returns = self.wallets['returns']
        sharpe = self.wallets['sharpe']
        weights = self.wallets.iloc[:, 3:]
        
        if method == 'sharpe_ratio':
            best_port_idx = np.array(sharpe).argmax()

        elif method == 'volatility':
            best_port_idx = np.array(vol).argmin()

        elif method == 'return':
            best_port_idx = np.array(returns).argmax()

        else:
            raise ValueError(
                f"method espera 'sharpe_ratio', 'volatility' ou 'return', não '{method}'"
            )

        return weights.iloc[best_port_idx]
