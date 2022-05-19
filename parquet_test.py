import pandas as pd

df = pd.read_parquet("company_tickers_exchange.parquet")

print(df.head())

ticker = 'AAPL'

print(type(df.loc[df['ticker'] == ticker]['cik'].values[0]))