import streamlit as st
from sec_api import QueryApi
import functions
import requests
import pandas as pd
import os

# Cargar la lista de industrias desde un archivo CSV
file_path = 'industry_list.csv' 
industrias = functions.read_industry_list(file_path)
print(industrias)


# Crear un estado de sesión para almacenar las selecciones
session_state = st.session_state
print(session_state)
if 'selected_industry' not in session_state:
    session_state.selected_industry = None
if 'selected_tickers' not in session_state:
    session_state.selected_tickers = []

# Título y subtítulo
st.title("SEC 10-K FinancialReportFetcher")
st.subheader("Extract key financial data with a single click")

# Selección de industria
selected_industry = session_state.selected_industry

selected_industry_index = 0 if selected_industry is None else industrias.index(selected_industry)

selected_industry = st.selectbox("Select an industry", industrias, index=selected_industry_index, key="industry_selectbox")
if selected_industry:
    st.write("Selected industry:", selected_industry)
    tickers = functions.get_tickers_by_industry(selected_industry)

    if tickers:
        ticker_names = [f"{item['ticker']} - {item['name']}" for item in tickers]
        ticker_names.insert(0, "Select All")
        selected_tickers = st.multiselect("Select tickers",ticker_names,
            default=[
            item
            for item in session_state.selected_tickers
            if item in ticker_names],
            key="tickers_multiselect")
        
        
        if "Select All" in selected_tickers:
            selected_tickers = [item['ticker'] for item in tickers]
        
        session_state.selected_industry = selected_industry
        session_state.selected_tickers = selected_tickers
        
        for item in tickers:
            if item['ticker'] in selected_tickers:
                st.write("Name:", item['name'])
                st.write("Ticker:", item['ticker'])
                
        folder_path = './reports'
        
        if st.button("Download Reports", key="download_button"):
            form_type_query = 'formType:("10-K") AND NOT formType:("10-K/A", "10-Q/A", NT)'
            ticker_query = functions.my_function(selected_tickers)
            date_range_query = 'filedAt:[2022-01-01 TO 2022-12-31]'  
            lucene_query = f"{form_type_query} AND {ticker_query} AND {date_range_query}"
            search_query = {
                "query": { "query_string": { "query": lucene_query } },
                "from": "0",
                "size": "200",
                "sort": [{ "filedAt": { "order": "desc" } }]
            }
            filings = functions.get_filings(search_query)
            urls = filings[['ticker', 'formType', 'periodOfReport', 'filedAt', 'linkToFilingDetails']].rename(columns={'linkToFilingDetails': 'filingUrl'})

            urls['financialReportsUrl'] = urls['filingUrl'].apply(lambda url: '/'.join(url.split('/')[:-1]) + '/Financial_Report.xlsx')

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            num_downloaded_reports = 0

            for _, row in urls.iterrows():
                try:
                    response = requests.get(row['financialReportsUrl'])
                    file_name = f"{row['ticker']}_{row['formType']}_{row['periodOfReport'].replace('/', '')}.xlsx"
                    file_path = os.path.join(folder_path, file_name)

                    with open(file_path, 'wb') as file:
                        file.write(response.content)

                    num_downloaded_reports += 1
                except Exception as e:
                    st.warning(f"❌ Error downloading report: {row['financialReportsUrl']}")
                    st.warning(str(e))

            st.success(f"✅ Downloaded {num_downloaded_reports} reports in {os.path.abspath(folder_path)}")   

    else:
        st.write("No tickers found for the selected industry")
else:
    st.write("No industry selected")
