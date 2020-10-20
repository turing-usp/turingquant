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


def get_fundamentus(ticker):
    """
    Essa função obtém os dados patrimoniais de empresas por meio do site `fundamentus.com.br`.
    """

    tickers = []
    if isinstance(ticker, str):
        tickers.append(ticker)
    elif isinstance(ticker, list):
        tickers = ticker
    else:
        return

    empresas = []

    base_url = "https://www.fundamentus.com.br/detalhes.php?papel="

    for ticker in tickers:
        print("Coletando informações de " + ticker)

        url = base_url + ticker
        try:
            response = requests.get(url)

            soup = BeautifulSoup(response.text, "html.parser")
            tabelas = soup.find_all('table', class_="w728")
            urls = soup.find_all('a')
        except:
            continue

        if len(tabelas) > 0:
            txt1 = list(BeautifulSoup(tabelas[0].prettify(),
                                      "html.parser").find_all("span", class_="txt"))
            txt2 = list(BeautifulSoup(tabelas[1].prettify(),
                                      "html.parser").find_all("span", class_="txt"))
            txt3 = list(BeautifulSoup(tabelas[2].prettify(),
                                      "html.parser").find_all("span", class_="txt"))
            txt4 = list(BeautifulSoup(tabelas[3].prettify(),
                                      "html.parser").find_all("span", class_="txt"))
            txt5 = list(BeautifulSoup(tabelas[4].prettify(),
                                      "html.parser").find_all("span", class_="txt"))
        else:
            continue

        # informações do papel
        papel = txt1[1].string.replace('\n    ', '').replace('\n   ', '')
        tipo = txt1[5].string.replace('\n    ', '').replace('\n   ', '')
        nomeEmpresa = txt1[9].string.replace('\n    ', '').replace('\n   ', '')
        setor = urls[14].string
        subsetor = urls[15].string
        vol_med_duas_sem = int(txt1[19].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        # informações de mercado
        valor_de_mercado = int(txt2[1].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        valor_da_firma = int(txt2[5].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        ult_balanco = txt2[3].string.replace('\n', '').replace(' ', '')
        nro_acoes = int(txt2[7].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        # indicadores
        lpa = float(txt3[6].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace(',', '.').replace('-', '0'))
        vpa = float(txt3[11].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace(',', '.').replace('-', '0'))
        marg_bruta = float(txt3[16].string.replace('\n', '').replace(' ', '').replace(
            '.', '').replace(',', '.').replace('%', '').replace('-', '0')) / 100
        marg_ebit = float(txt3[21].string.replace('\n', '').replace(' ', '').replace(
            '.', '').replace(',', '.').replace('%', '').replace('-', '0')) / 100
        marg_liquida = float(txt3[26].string.replace('\n', '').replace(' ', '').replace(
            '.', '').replace(',', '.').replace('%', '').replace('-', '0')) / 100
        ebit_ativo = float(txt3[31].string.replace('\n', '').replace(' ', '').replace(
            '.', '').replace(',', '.').replace('%', '').replace('-', '0')) / 100
        roic = float(txt3[36].string.replace('\n', '').replace(' ', '').replace(
            '.', '').replace(',', '.').replace('%', '').replace('-', '0')) / 100
        div_yield = float(txt3[39].string.replace('\n', '').replace(' ', '').replace(
            '.', '').replace(',', '.').replace('%', '').replace('-', '0')) / 100
        roe = float(txt3[41].string.replace('\n', '').replace(' ', '').replace(
            '.', '').replace(',', '.').replace('%', '').replace('-', '0')) / 100
        ev_ebit = float(txt3[44].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace(',', '.').replace('-', '0'))
        liquidez_corr = float(txt3[46].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace(',', '.').replace('-', '0'))
        giro_ativos = float(txt3[49].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace(',', '.').replace('-', '0'))
        divBr_patr = float(txt3[51].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace(',', '.').replace('-', '0'))
        cresc_rec = float(txt3[54].string.replace('\n', '').replace(' ', '').replace(
            '.', '').replace(',', '.').replace('%', '').replace('-', '0')) / 100
        # balanço patrimonial
        ativo = int(txt4[2].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        div_bruta = int(txt4[4].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        disponibilidades = int(txt4[6].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        div_liquida = int(txt4[8].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        ativo_circulante = int(txt4[10].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        patr_liquido = int(txt4[12].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        # demonstrativos de resultado
        rec_liq_12m = int(txt5[4].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('.', '').replace('-', '0'))
        rec_liq_3m = int(txt5[6].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('.', '').replace('-', '0'))
        ebit_12m = int(txt5[8].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        ebit_3m = int(txt5[10].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        lucro_liq_12m = int(txt5[12].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))
        lucro_liq_3m = int(txt5[14].string.replace('\n', '').replace(
            ' ', '').replace('.', '').replace('-', '0'))

        empresa = {"Ticker": papel, "Tipo": tipo, "Nome": nomeEmpresa,
                   "Setor": setor, "Subsetor": subsetor,
                   "Vol méd (2m)": vol_med_duas_sem,
                   "Valor de mercado": valor_de_mercado,
                   "Valor da firma": valor_da_firma,
                   "Ult. Balanço": ult_balanco,
                   "Nro. Ações": nro_acoes, "LPA": lpa, "VPA": vpa,
                   "Margem Bruta": marg_bruta, "Margem EBIT": marg_ebit,
                   "Margem Líquida": marg_liquida, "EBIT por ativo": ebit_ativo,
                   "ROIC": roic, "Div. Yield": div_yield, "ROE": roe,
                   "EV/EBIT": ev_ebit, "Liquidez Corr.": liquidez_corr,
                   "Giro Ativos": giro_ativos, "Divida bruta/Patr.": divBr_patr,
                   "Cresc. Rec (5a)": cresc_rec, "Ativo": ativo,
                   "Dívida bruta": div_bruta, "Dívida líquida": div_liquida,
                   "Disponibilidades": disponibilidades,
                   "Ativo circulante": ativo_circulante,
                   "Patrim. Líquido": patr_liquido,
                   "Receita Líq. 12m": rec_liq_12m,
                   "Receita Líq. 3m": rec_liq_3m, "EBIT 12m": ebit_12m,
                   "EBIT 3m": ebit_3m, "Lucro Líq. 12m": lucro_liq_12m,
                   "Lucro Líq. 3m": lucro_liq_3m}
        empresas.append(empresa)

        time.sleep(1)

    df = pd.DataFrame(empresas)
    return df


def get_tickers(setor="Todos"):
    """
    Essa função obtém os tickers listados no site fundamentus.com.br, seja um setor
    específico, uma lista de setores ou todos os tickers de todos os setores.
    """

    setores = {"Agropecuária": "42", "Água e Saneamento": "33", "Alimentos": "15",
               "Bebidas": "16", "Comércio": "27", "Comércio2": "12",
               "Comércio e Distribuição": "20", "Computadores e Equipamentos": "28",
               "Construção e Engenharia": "13", "Diversos": "26",
               "Embalagens": "6", "Energia Elétrica": "32",
               "Equipamentos Elétricos": "9", "Exploração de Imóveis": "39",
               "Financeiros": "35", "Fumo": "17", "Gás": "34",
               "Holdings Diversificadas": "40", "Hoteis e Restaurantes": "24",
               "Madeira e Papel": "5", "Máquinas e Equipamentos": "10",
               "Materiais Diversos": "7", "Material de Transporte": "8",
               "Mídia": "23", "Mineração": "2", "Outros": "41",
               "Petróleo, Gás e Biocombustíveis": "1", "Previdência e Seguros": "38",
               "Prods. de Uso Pessoal e de Limpeza": "18", "Programas e Serviços": "29",
               "Químicos": "4", "Saúde": "19", "Securitizadoras de Recebíveis": "36",
               "Serviços": "11", "Serviços Financeiros Diversos": "37",
               "Siderurgia e Metalurgia": "3", "Tecidos, Vestuário e Calçados": "21",
               "Telefonia Fixa": "30", "Telefonia Móvel": "31", "Transporte": "14",
               "Utilidades Domésticas": "22", "Viagens e Lazer": "25"}

    lista_setores = []
    if setor == "Todos":
        lista_setores = list(setores.keys())
    elif isinstance(setor, str):
        if setores in setor:
            lista_setores.append(ticker)
        else:
            print("Esse setor não existe")
            return []
    elif isinstance(setor, list):
        lista_setores = setor
    else:
        return []

    tickers = []

    for item in lista_setores:
        try:
            url = "https://www.fundamentus.com.br/resultado.php?setor=" + \
                setores[item]
            response = requests.get(url)
        except:
            print("Não foi possível coletar informações do setor: " + item)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        tickers_bruto = soup.find('tbody').find_all("a")
        for ticker in tickers_bruto:
            tickers.append(ticker.string)

    tickers.sort()
    return tickers


def get_ibov(atual=True):
    """
    Essa função obtém a composição atual do Índice Bovespa
    """

    empresas = []

    if atual:
        url = "http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraQuadrimestre.aspx?Indice=IBOV&idioma=pt-br"
        print("Coletando informações da B3")

        soup = ''

        try:
            response = requests.get(url)

            soup = BeautifulSoup(response.text, "html.parser")
        except:
            return None

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
                    empresa = {'Ticker': ticker, 'Nome': nome, 'Tipo': tipo,
                               'Quantidade': qtde, 'Part.': part}

                    empresas.append(empresa)
            else:
                continue

    return pd.DataFrame(empresas)


def get_financials(url):
    page_source = requests.get(url)

    soup_html = BeautifulSoup(page_source.text, 'html.parser')
    table_soup = soup_html.find(
        'div', class_="M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)")

    # Get Title Row
    headlines = table_soup.find('div', class_="D(tbr) C($primaryColor)")
    headlines = headlines.findAll('span')
    title_row = list()
    for line in headlines:
        title_row.append(line.text)

    table = pd.DataFrame(None, columns=title_row)
    remaining_lines = table_soup.findAll(
        'div', class_="D(tbr) fi-row Bgc($hoverBgColor):h")
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


def get_income_statement(symbol):
    url = 'https://finance.yahoo.com/quote/' + symbol + '/financials'
    return get_financials(url).drop(['ttm'], axis=0)


def get_balance_sheet(symbol):
    url = 'https://finance.yahoo.com/quote/' + symbol + '/balance-sheet'
    return get_financials(url)


def get_cashflow(symbol):
    url = 'https://finance.yahoo.com/quote/' + symbol + '/cash-flow'
    return get_financials(url).drop(['ttm'], axis=0)


def get_sp500_tickers():
    """
    Essa função obtem todas o ticker de todas as ações do S&P 500.
    """
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(resp.text, 'html.parser')
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
