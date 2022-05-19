import requests
import csv 
import json
import pandas as pd
#Contains methods for creating EDGAR reference files 
#https://www.sec.gov/edgar/sec-api-documentation

cte_url = 'https://www.sec.gov/files/company_tickers_exchange.json'

with open('company_tickers_exchange.json', "w") as f:

    response = requests.get(cte_url)
    json_data = response.json()
    json.dump(json_data, f)

#print(json_data['data'][:5])
cte_df = pd.json_normalize(json_data, record_path=['data'])
cte_df.columns = json_data['fields']
print(cte_df.head())
print(type(cte_df))

cte_df.to_parquet('company_tickers_exchange.parquet')

df = pd.read_parquet('company_tickers_exchange.parquet')

df.head()