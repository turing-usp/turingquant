"""Módulo para coletar informações de ações do mercado financeiro."""

import pandas as pd
import numpy as np

import datetime
import time

import requests
from alpha_vantage.timeseries import TimeSeries
from bs4 import BeautifulSoup
import yfinance as yf


def daily(key, ticker, br=True):
    """
    Essa função entrega a cotação dia a dia de um produto negociado
    em bolsa com melhor formatação de dados que a biblioteca
    alpha_vantage.

    Args:
        key (str): recebe a chave de uso do AlphaVantage
        ticker (str): recebe o ticker do papel que será obtido
        br (str): se `True`, adiciona ".SA" ao final do ticker, necessário para papéis brasileiros

    Returns:
        pd.DataFrame: um dataframe contendo a cotação dia a dia do ativo.
    """

    if br:
        ticker = ticker + ".SA"

    ts = TimeSeries(key=key, output_format='pandas')

    try:
        data, meta_data = ts.get_daily_adjusted(
            symbol=ticker, outputsize='full')
    except:
        print("Couldn't get data, check if you passed the ticker correctly")
        return

    data.rename(columns={"1. open": "Open", "2. high": "High", "3. low": "Low",
                         "4. close": "Close", "5. adjusted close": "Adj Close",
                         "6. volume": "Volume", "7. dividend amount": "Dividend Amount",
                         "8. split coefficient": "Split Coefficient"},
                inplace=True)
    data.index = pd.to_datetime(data.index)
    return data


def intraday(key, ticker, br=True, interval="1min"):
    """
    Essa função entrega a cotação intraday dos últimos 5 dias de
    um produto negociado em bolsa com melhor formatação de dados que a
    biblioteca alpha_vantage.

    Args:
        key (str): recebe a chave de uso do AlphaVantage
        ticker(str): recebe o ticker do papel que será obtido
        br(bool): se `True`, adiciona ".SA" ao final do ticker, necessário para papeis brasileiros.
        interval(str): recebe o período entre cada informação (1min, 5min, 15min, 30min, 60min)

    Returns:
        pd.DataFrame: DataFrame contendo a cotação intraday dos últimos 5 dias.
    """

    ts = TimeSeries(key=key, output_format='pandas')

    if br:
        ticker = ticker + ".SA"

    try:
        data, meta_data = ts.get_intraday(symbol=ticker,
                                          interval=interval, outputsize='full')
    except:
        print("Couldn't get data, check if you passed the ticker correctly")
        return

    data.rename(columns={"1. open": "Open", "2. high": "High", "3. low": "Low",
                         "4. close": "Close", "5. volume": "Volume"},
                inplace=True)
    data.index = pd.to_datetime(data.index) + datetime.timedelta(hours=1)

    return data


def get_fundamentus(tickers):
    """
    Essa função obtém os dados patrimoniais de empresas por meio do site fundamentus.com.br,
    voltado para companias com papeis na B3.

    Args:
        tickers (str / list): string com tickers separados por espaço ou lista de tickers
        
    Returns:
        pd.DataFrame: dataframe contendo os dados patrimoniais (linhas) para os tickers dados (colunas)
    """

    def fix_type(value):
        if isinstance(value, str):
            if value[-1] == '%':
                value = value.replace(',', '.')
                value = float(value[ :-1]) / 100
            elif value == '-':
                value = np.nan
        return value

    def format_keys(label):
        to_replace = {
            '?':'',   '$':'',   '.':'',
            '(':'',   ')':'',   ' / ':'/',
            '/ ':'/',

            'í':'i', 'ú':'u', 'ã':'a',
            'é':'e', 'õ':'o', 'ó':'o',
            'ç':'c',

            'balanco processado':'balanco data',
            'data ult cot':'cotacao data',
            'vol  med':'volume medio',

            '52 sem':'12m', '12 meses':'12m',
            '30 dias':'1m', 'dia':'1d'
        }

        label = label.lower()
        for char in list(to_replace.keys()):
            label = label.replace(char, to_replace[char])
        return label

    
    if isinstance(tickers, str):
        tickers = tickers.split()
    
    if not isinstance(tickers, list):
        raise TypeError(f"Espera-se string ou lista de strings para `tickers`, não {type(tickers)}.")

    base = "https://www.fundamentus.com.br/detalhes.php?papel="
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0)'}
    final_df = pd.DataFrame()

    for ticker in tickers:
        print(f"Coletando informações de '{ticker}'...")

        url = base + ticker
        response = requests.get(url, headers=header)
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all('table', class_="w728")
        time.sleep(1)

        if len(tables) == 0:
            print(f"Nenhum papel '{ticker}' encontrado.")
            continue
        
        keys = pd.Series(dtype=str)
        values = pd.Series(dtype=str)

        for t in range(len(tables)):
            table = tables[t]
            df = pd.read_html(str(table), thousands='.', decimal=',')[0]
            
            if t == 2:
                df.drop(0, axis=0, inplace=True)
                df[0] = df.apply(lambda row: 'oscilacao ' + str(row[0]), axis=1)                
            elif t == 3:
                df.drop(0, axis=0, inplace=True)
            elif t == 4:
                df.drop([0, 1], axis=0, inplace=True)
                df[0] = df.apply(lambda row: row[0] + ' 12m', axis=1)
                df[2] = df.apply(lambda row: row[2] + ' 3m', axis=1)

            for c in range(0, df.shape[1], 2):
                keys = pd.concat([keys, df.iloc[ : , c]], axis=0, ignore_index=True)
                values = pd.concat([values, df.iloc[ : , c+1]], axis=0, ignore_index=True)

        company = pd.DataFrame({'keys':keys, ticker:values})
        company[ticker] = company.apply(lambda row: fix_type(row[ticker]), axis=1)
   
        if final_df.empty:
            final_df = company.copy()
            continue

        final_df = final_df.join(company.set_index('keys'), how='outer', on='keys')
    
    if not final_df.empty:
        final_df['keys'] = final_df.apply(lambda row: format_keys((row['keys'])), axis=1)
        final_df.set_index('keys', inplace=True, drop=True)
        final_df.index.name = None

        final_df.drop(['papel', 'oscilacao mês'], inplace=True, axis=0)
        final_df.dropna(how='all', inplace=True)

        pd.set_option("max_rows", final_df.shape[0])

    return final_df


def get_tickers(setores="Todos"):
    """
    Essa função obtém os tickers listados no site fundamentus.com.br consoante seus setores.
    Observação: o 'setor' no site fundamentus.com.br corresponde ao 'subsetor' na B3,
    e o 'subsetor' nesse site corresponde ao 'segmento' na B3.

    Args:
        setores (str / list): 'Todos' para considerar todos os setores ou lista com os setores desejados
        
    Returns:
        list: lista com todos os tickers listados para os setores pedidos

    """

    setores_dict = {
        'Agropecuária': 1,
        'Água e Saneamento': 2,
        'Alimentos Processados': 3,
        'Análises e Diagnósticos': 4,
        'Automóveis e Motocicletas': 5,
        'Bebidas': 6,
        'Comércio': 7,
        'Comércio e Distribuição': 8,
        'Computadores e Equipamentos': 9,
        'Construção Civil': 10,
        'Construção e Engenharia': 11,
        'Diversos': 12,
        'Embalagens': 13,
        'Energia Elétrica': 14,
        'Equipamentos': 15,
        'Exploração de Imóveis': 16,
        'Gás': 17,
        'Holdings Diversificadas': 18,
        'Hoteis e Restaurantes': 19,
        'Intermediários Financeiros': 20,
        'Madeira e Papel': 21,
        'Máquinas e Equipamentos': 22,
        'Materiais Diversos': 23,
        'Material de Transporte': 24,
        'Medicamentos e Outros Produtos': 25,
        'Mídia': 26,
        'Mineração': 27,
        'Outros': 28,
        'Petróleo, Gás e Biocombustíveis': 30,
        'Previdência e Seguros': 31,
        'Produtos de Uso Pessoal e de Limpeza': 32,
        'Programas e Serviços': 33,
        'Químicos': 34,
        'Serviços Diversos': 36,
        'Serviços Financeiros Diversos': 37,
        'Siderurgia e Metalurgia': 38,
        'Tecidos, Vestuário e Calçados': 39,
        'Telecomunicações': 40,
        'Transporte': 41,
        'Utilidades Domésticas': 42,
        'Viagens e Lazer': 43
    }

    if setores == 'Todos':
        setores = list(setores_dict.keys())

    if not isinstance(setores, list):
        raise ValueError(f"Espera-se 'Todos' ou lista de strings para `setores`, não {setores}.")

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0)'}
    base = "https://www.fundamentus.com.br/resultado.php?setor="
    tickers = []

    for setor in setores:
        if setor in setores_dict:
            time.sleep(1)
            url = base + str(setores_dict[setor])
            response = requests.get(url, headers=header)
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find('tbody').find_all("a")

            for link in links:
                ticker = link.text
                tickers.append(ticker)
        else:
            print(f"Setor '{setor}' não encontrado.")
            continue

    tickers.sort()

    return tickers


def get_ibov():
    """
    Essa função obtém informações sobre a composição atual do Índice Bovespa
    por meio do site da B3.

    Returns:
        pd.DataFrame: dataframe contendo ticker, nome, tipo, quantidade e participação 
        das companias constituintes do índice
    """

    empresas = []

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0)'}
    url = "http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraQuadrimestre.aspx?Indice=IBOV&idioma=pt-br"
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, "html.parser")

    print("Coletando informações da B3...")

    for i in range(100):
        id_linha = 'ctl00_contentPlaceHolderConteudo_grdResumoCarteiraPrevia_ctl00__' + \
            str(i)
        linha = soup.find_all(id=id_linha)
        info = []
        if len(linha) > 0:
            info = list(BeautifulSoup(str(linha), "html.parser").find_all(
                "span", class_="label"))
            if len(info) == 5:
                try:
                    ticker = info[0].string
                    nome = info[1].string
                    tipo = info[2].string
                    qtde = float(info[3].string.replace('.', ''))
                    part = float(info[4].string.replace(',', '.'))
                except:
                    continue

        if part < 99.0:
            if len(info) > 0:
                empresa = {
                    'Ticker':ticker,
                    'Nome':nome,
                    'Tipo':tipo, 
                    'Quantidade':qtde,
                    'Part.':part
                }
                empresas.append(empresa)
        else:
            continue

    return pd.DataFrame(empresas)


def get_financials(url):
    """
    Função de suporte, base para as funções get_income_statement(), get_balance_sheet()
    e get_cashflow().
    """

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0)'}
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    table_soup = soup.find('div', class_="M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)")

    # Get Title Row
    headlines = table_soup.find('div', class_="D(tbr) C($primaryColor)")
    headlines = headlines.findAll('span')
    title_row = list()

    for line in headlines:
        title_row.append(line.text)

    table = pd.DataFrame(None, columns=title_row)
    remaining_lines = table_soup.findAll('div', class_="D(tbr) fi-row Bgc($hoverBgColor):h")

    for row in remaining_lines:
        columns = row.findChildren('div', recursive=False)
        line_values = list()
        for col in columns:
            if ',' in col.text:
                value = float(col.text.replace(',', ''))
            elif '-' in col.text and len(col.text) == 1:
                value = np.nan
            else:
                value = col.text                
            line_values.append(value)
        table.loc[len(table)] = line_values

    table = table.set_index(title_row[0])

    return table.T


def get_income_statement(ticker, br=True):
    """
    Obtém o Income Statement ou a Demonstração do Resultado do Exercício (DRE)
    para a companhia do ticker desejado por meio do Yahoo! Finance.

    Args:
        ticker (str): recebe o ticker do papel que será obtido
        br (str): se `True`, adiciona ".SA" ao final do ticker, necessário para papéis brasileiros
        
    Returns:
        pd.DataFrame: dataframe com os dados do relatório nos últimos anos.
    """
    
    if br:
        ticker = ticker + '.SA'
    url = 'https://finance.yahoo.com/quote/' + ticker + '/financials'
    
    return get_financials(url).drop(['ttm'], axis=0)


def get_balance_sheet(ticker, br=True):
    """
    Obtém o Balance Sheet ou o Balanço Patrimonial para a companhia do ticker desejado
    por meio do Yahoo! Finance.

    Args:
        ticker (str): recebe o ticker do papel que será obtido
        br (str): se `True`, adiciona ".SA" ao final do ticker, necessário para papéis brasileiros
        
    Returns:
        pd.DataFrame: dataframe com os dados do relatório nos últimos anos.
    """

    if br:
        ticker = ticker + '.SA'        
    url = 'https://finance.yahoo.com/quote/' + ticker + '/balance-sheet'

    return get_financials(url)


def get_cash_flow(ticker, br=True):
    """
    Obtém o Cash Flow ou o Fluxo de Caixa para a companhia do ticker desejado
    por meio do Yahoo! Finance.

    Args:
        ticker (str): recebe o ticker do papel que será obtido
        br (str): se `True`, adiciona ".SA" ao final do ticker, necessário para papéis brasileiros
        
    Returns:
        pd.DataFrame: dataframe com os dados do relatório nos últimos anos.
    """

    if br:
        ticker = ticker + '.SA'
    url = 'https://finance.yahoo.com/quote/' + ticker + '/cash-flow'

    return get_financials(url).drop(['ttm'], axis=0)


def get_sp500_tickers():
    """
    Essa função obtém os tickers de todas as atuais constituientes do S&P500.

    Returns:
        list: lista com todos os tickers atuais do índice.
    """

    response = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable sortable'})

    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)

    tickers = [s.replace('\n', '') for s in tickers]

    return tickers


def get_annual_hpr(ticker, period=252):
    """
    Essa função calcula o holding period return anual de junho
    """

    stock = yf.Ticker(ticker)

    stock_data = stock.history(period="max")

    dividends = stock_data['Dividends']
    close_prices = stock_data['Close']

    dividend_period_sum = dividends.copy()

    for row in range(period, len(dividends)):
        dividend_period_sum.iloc[row] = dividends.iloc[row-period:row].sum()

    dividend_semesterly_sum = dividend_period_sum.resample("2Q").last().ffill()
    close_semesterly_prices = close_prices.resample("2Q").last().ffill()

    isJune = dividend_semesterly_sum.index.month.isin([6])

    income = dividend_semesterly_sum[isJune]
    value = close_semesterly_prices[isJune]

    holding_period_return = (
        income + value - value.shift(-1)) / value.shift(-1)

    return holding_period_return
