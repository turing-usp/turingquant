from setuptools import setup

setup(
    name="Quant_Utils",
    version="0.1.0",
    py_modules=["metrics", "benchmark", "support"],

    install_requires=["pandas", "pandas_datareader", "numpy", "matplotlib", "alpha_vantage", "bs4"],

    author="Grupo Turing",
    author_email="turing.usp@gmail.com",
    description="Ferramentas para obtenção e manipulação de dados financeiros.",
    keywords="quant data scraping quantitative finance benchmark backtest",
    url="https://grupoturing.com.br",
    project_urls={
        "Source Code": "https://github.com/GrupoTuring/Quant-Utils"
    }
)
