# Turing Quant

`turingquant` é uma biblioteca para coleta, análise e backtesting de ativos e estratégias financeiras. O projeto está em desenvolvimento ativo pelos membros de Finanças Quantitativas do [Turing USP](https://github.com/turing-usp).

`pip install turingquant` instala a última versão estável.

## Utilização

A biblioteca conta com 3 módulos: `metrics`, `benchmark`, `support` e `plot_metrics`.

`support` possui funções para obter dados fundamentalistas de empresas.

`metrics` possui funções para obter informações e indicadores sobre uma série de retornos.

`benchmark` possui funções para calcular o retorno de um ativo em um dado intervalo de tempo.

`optimizers` possui classes para otimizações de carteiras de investimento.

A API de onde obtemos os dados fundamentalistas é a Alpha Vantage e você pode obter a [chave de uso gratuitamente](https://www.alphavantage.co/support/#api-key). Essa chave será necessária sempre que você utilizar as funções `daily` e `intraday`.

No código você pode verificar o que cada função retorna e a descrição de cada parâmetro que as funções recebem.

## Contribuidores

- [Gabriel Mossato](https://github.com/gvmossato)
- [Guilherme Colasante Sgarbiero](https://github.com/guicola-sg)
- [Guilherme Corazza Marques](https://github.com/guicmarques)
- [Guilherme Fernandes](https://github.com/aateg)
- [Julia Pocciotti](https://github.com/juliapocciotti)
- [Lucas Leme](https://github.com/lucas-leme)
- [Noel Viscome Eliezer](https://github.com/anor4k)
