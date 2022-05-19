#Testing how t download edgar thingys

import requests
#Need to make user agent whatever thing
aapl_cik = 320193

response = requests.get(f"https://data.sec.gov/submissions/CIK{aapl_cik:010d}.json")

print(response.json())

import streamlit as sst 

col1, col2 = basic_info_container.columns(2)
with col1:
    basic_info_container.subheader("The Company")
    try:
        basic_info_container.subheader('{}'.format(tick.info['longName']))
    except KeyError:
        basic_info_container.warning('Yahoo Finance Key Error, double check ticker')
    except:
        basic_info_container.warning('Not key error, something is broken')
    basic_info_container.image(tick.info["logo_url"])
    basic_info_container.write(tick.info["sector"])
    basic_info_container.write(tick.info["industry"])
    website = tick.info["website"]
    basic_info_container.write("[Company Website]({})".format(website))
    if market == 'ASX':
        asx_website = "https://www2.asx.com.au/markets/company/" + tic
        basic_info_container.write("[ASX Link]({})".format(asx_website))
    elif market == 'NYSE/NASDAQ':
        cte_df = pd.read_parquet("company_tickers_exchange.parquet")
        cik = cte_df.loc[cte_df['ticker'] == tic]['cik'].values[0]
        edgar_result = f"https://www.sec.gov/edgar/browse/?CIK={cik:010d}&owner=exclude"
        basic_info_container.write("[SEC Link]({})".format(edgar_result))

    
with col2:
    basic_info_container.write(tick.info["longBusinessSummary"])
