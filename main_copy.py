import yfinance as yf
import streamlit as st 
import pandas as pd 
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns

#Maybe change mutation allowance when I learn what that means
@st.cache(allow_output_mutation=True)
def ticker(ticker: str):
    return yf.Ticker(ticker)

#-----------------------------------Sidebar Radio Buttons for stock and info selection
# https://www.sec.gov/edgar/sec-api-documentation
with st.sidebar:
    with st.form(key = 'ticker_form'):
        #Market and Stock CHoice
        market = st.radio(
            'Choose stock exchange:',
            ('NYSE/NASDAQ', 'ASX')
        )

        exchanges = {'NYSE/NASDAQ' : '', 'ASX' : '.AX'}
        tic = st.text_input("Ticker", value = "AAPL")
        tic = tic.upper()

        ti = tic + exchanges[market]
        tick = ticker(ti)
        submitted = st.form_submit_button('Submit')

        #Choose tabs of info to display
    to_display = st.radio(
        'Data Options',
        ('Basic Info', 'Metrics','Ownership & Management')
        )
    
    ann_or_qrtr = st.radio(
        'Annual or Quarterly Reports',
        ('Annual', 'Quarterly')
    )


#Title
st.title('Stock Fundamentals')
st.text('''Focus on the fundamentals: 
    - Return on Invested Capital 
    - Enterprise Value/EBITDA
    - Management interests 
    - Narrative''')

#--------------------------------Basic info & Links to Govt Sites


def basic_info_f():
    basic_info_container = st.container()
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


#Quick and dirty EBITDA - Capex = EBIT, try to get EBITDA - maint. Capex
# Use Enterprise Value (EV). Enterprise Value = Market Cap + Total Debt - Cash
# Enterprise Value to Sales 
# EV/EBIT 

  
#---------------------------------------------------------Metrics 
def metrics_f(tick = tick):
    st.subheader('Ratios & Basic Numbers')
    recent_year_f = tick.financials.iloc[:, 0]
    recent_year_b = tick.balance_sheet.iloc[:, 0]
    recent_year_c = tick.cashflow.iloc[:, 0]

    ebit = recent_year_f.loc['Ebit']
    mcap = tick.info['marketCap']
    debt = tick.info['totalDebt']
    cash = tick.info['totalCash']
    nta = recent_year_b['Net Tangible Assets']
    ev = tick.info['enterpriseValue']

    #Things for Greenblatt Return on Capital
    #Return on Capital = EBIT/(Net Fixed Assets + Working Capital)
    #https://einvestingforbeginners.com/return-on-capital-daah/
    fixed_assets = recent_year_b['Property Plant Equipment']
    op_inc = recent_year_f['Operating Income']

    curr_ass = recent_year_b['Total Current Assets']
    curr_liab = recent_year_b['Total Current Liabilities']
    wcap = curr_ass - curr_liab
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label = 'Market Cap (m)',value =  round(mcap/1000000,2))
        st.metric(label = 'Debt (m) ', value = round(debt/1000000, 2))
        st.metric(label = 'Cash (m)', value = round(cash/1000000,2))
    with col2:
        st.metric(label = 'EV (m)', value =  round(ev/1000000,2))
        st.metric('EV/EBIT ', round(ev/ebit, 2) )
        #Greenblatt yield Operating Income/Enterprise Value
        st.metric('Yield %', round(ebit/ev * 100,2))
    with col3:
        #Greenblatt ROC EBIT/ (Net Working Capital + Fixed Assets)
        st.metric('Return on Capital', round((ebit/(wcap + fixed_assets)),2))


#-------------------------------------------------------Financials Chart  
def financials_chart():
    all_f = pd.concat([tick.financials, tick.balance_sheet, tick.cashflow])

    options = st.multiselect('Choose elements to graph', all_f.index.tolist(), ['Total Revenue', 'Ebit', 'Common Stock'])
    options_q = [x + ':Q' for x in options]

    chart_data = all_f.loc[options, :].T.reset_index().rename({'':'date'}, axis = 'columns')
    melted_chart_data = chart_data.melt('date', var_name = 'choices', value_name= 'amount')

    #https://altair-viz.github.io/gallery/grouped_bar_chart.html
    chart = alt.Chart(melted_chart_data).mark_bar().encode(
        x = 'year(date):O',
        y = 'amount:Q',
        column = alt.Column('choices:O', header = alt.Header(title = 'choices:O')),
        color = alt.Color('choices:O', legend = alt.Legend(title = 'Choices'), scale = alt.Scale(scheme = 'tableau20'))

        
    )

    chart

#----------------------------Match statement to display info from sidebar
#('Basic Info', 'Metrics','Ownership & Management')
match to_display:
    case 'Basic Info':
        basic_info_f()
    case 'Metrics':
        metrics_f()
    case 'Ownership & Management':
        st.write("TODO")

#if to_display == 'Basic Info':
#    basic_info_f()
#else:
#    metrics_f()
#metrics_f()
financials_chart()
#----------------------------------------------------------------
#TODO Finish formatting thins into options, probably do all the inside ownership and management 
#into one

#st.write([x + ':Q' for x in options])
#st.write(all_f.reset_index().loc[:, 'index'])

#st.subheader('Financials')
#st.dataframe(tick.financials.style.background_gradient(cmap = 'Blues'))

#st.subheader('Info')
#st.write(tick.info)



st.subheader('Cashflow')
st.write(tick.cashflow)

st.subheader('Balance Sheet')
st.write(tick.balance_sheet)

st.subheader('Earnings')
st.write(tick.earnings)



#Major Holders Barchart
st.subheader('Major Holders')
st.write(tick.major_holders)

holders = tick.major_holders
holders.drop(holders.tail(2).index, inplace = True) # Drop last rows 
holders[0] = holders[0].apply(lambda x: float(x[:-1])) #Turning % into Float
general_public = 100 - holders[0].sum() #Calculate percentage owned by others
holders.loc[2] = pd.Series([general_public, r"% of Shares Held By Others"]) #Add other row

#TODO fix the Major holders chart!!

#st.bar_chart(holders.transpose())
#plt.ylabel(r'% Owned')
#plt.title('Major Holders')
#bars = alt.Chart(holders).mark_bar().encode(
#    x=alt.X('sum(0):Q', stack = 'zero'),
#    color=alt.Color('1:N')
#
#).properties(
#    width = 800,
#    height = 300
#)
#text = alt.Chart(holders).mark_text(dx=-15, dy=3, color = 'white').encode(
#    x=alt.X('sum(0):Q', stack = 'zero'),
#    detail = '1:N',
#    text = alt.Text('sum(0):Q', format ='.1f')
#).properties(
#    width = 800,
#    height = 300
#)
#alt_plot =  bars + text
#st.altair_chart(alt_plot)

#-----------------------------------Useful tables and such for now 
recent_year_f
recent_year_b

