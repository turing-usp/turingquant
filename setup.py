from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="turingquant",
    version="0.2.2",
    packages=find_packages(),
    install_requires=["pandas", "pandas_datareader", "numpy", "matplotlib", "alpha_vantage", "bs4", "plotly", "yfinance"],

    author="Grupo Turing",
    author_email="turing.usp@gmail.com",
    description="Ferramentas para obtenção e manipulação de dados financeiros.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="quant data scraping quantitative finance benchmark backtest",
    url="https://grupoturing.com.br",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Source Code": "https://github.com/GrupoTuring/turingquant"
    },
    python_requires='>=3.6'
)
