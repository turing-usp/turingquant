# README

Esse repositório tem a intenção de ajudar os membros do Grupo Turing Quant a obter dados sobre cotações de ações e dados de mercado, como balanços de empresas e algumas outras informações sobre o mercado financeiro.

## Uso

Para seu pleno uso, são necessárias algumas outras bibliotecas e credenciais. Para isso use o pip para instalar alguns pacotes em seu environment:

`pip install pandas alpha-vantage beautifulsoup4`

A API de onde obtemos os dados de mercado é a Alpha Vantage e você pode obter a [chave de uso gratuitamente](https://www.alphavantage.co/support/#api-key). Essa chave será necessária sempre que você utilizar as funções `daily` e `intraday`.

## Funções
Por enquanto o helper tem as seguintes funções:

- `daily` - fornece cotação diária de todos os ativos negociados em bolsa
- `intraday` - fornece cotação minuto a minuto dos últimos 5 dias de negociação
- `get_fundamentus` - obtém dados do site fundamentus.com.br sobre uma ação ou lista de ações
- `get_tickers` - obtém todos os tickers negociados na B3 à partir do fundamentus
- `get_ibov` - obtém a última carteira do Índice Ibovespa

No código você pode verificar o que cada função retorna e a descrição de cada parâmetro que as funções recebem.

## Feito por:
- [Guilherme Corazza Marques](https://github.com/guicmarques)
- [Noel Viscome Eliezer](https://github.com/anor4k)
- [Guilherme Fernandes](https://github.com/aateg)
- [Lucas Leme](https://github.com/lucas-leme)