import streamlit as st
from sec_api import QueryApi
import requests
import functions
import shutil
import base64
import requests
import csv
import pandas as pd
import os



# Cargar la lista de industrias desde un archivo CSV
listado_industrias = 'industry_list.csv' 
industrias = functions.read_industry_list(listado_industrias)

archivo_csv = 'tickers_list.csv'
# Crear una lista para almacenar los diccionarios
listado_tickers = []
# Leer el archivo CSV y convertirlo en una lista de diccionarios
with open(archivo_csv, 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        listado_tickers.append(dict(row))


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

    if listado_tickers:
        ticker_names = [f"{item['ticker']} - {item['name']}" for item in listado_tickers]
        ticker_names.insert(0, "Select All")
        selected_tickers = st.multiselect("Select tickers",ticker_names,
            default=[
            item
            for item in session_state.selected_tickers
            if item in ticker_names],
            key="tickers_multiselect")
        
        selected_industry_tickers = [item['ticker'] for item in listado_tickers if item['industry'] == selected_industry]
        
        if "Select All" in selected_tickers:
            selected_tickers = selected_industry_tickers

        session_state.selected_industry = selected_industry
        session_state.selected_tickers = selected_tickers

        if set(selected_tickers) == set(selected_industry_tickers):
            st.write("You have selected all tickers for the industry", selected_industry)
            st.write("Total tickers:", len(selected_industry_tickers))
        else:
            for item in listado_tickers:
                if item['ticker'] in selected_tickers:
                    st.write("Name:", item['name'])
                    st.write("Ticker:", item['ticker'])
        
        ruta_descarga = r'C:/SEC/tickers_10K'

        if not os.path.exists(ruta_descarga):
            os.makedirs(ruta_descarga)

        username = 'MV-Data'
        repository = 'SEC_Fetcher'
        #path = "blob/master/reports/01-01-2022%20al%2031-12-2022"
        path = "reports/01-01-2022 al 31-12-2022"
        access_token = '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'

        if st.button("Descargar informes"):
            if selected_tickers:
                progress_bar = st.progress(0)  # Barra de progreso inicializada en 0
                status_text = st.empty()  # Espacio para el texto de estado
                descargas_exitosas = 0
                total_tickers = len(selected_tickers)  # Total de tickers seleccionados
                tickers_descargados = []
            
                for i, ticker_info in enumerate(selected_tickers, 1):
                    ticker = ticker_info.split('-')[0].strip()
                    api_url = f"https://api.github.com/repos/{username}/{repository}/contents/{path}/{ticker}.xlsx"
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = requests.get(api_url, headers=headers)

                    if response.status_code == 200:
                        download_url = response.json().get("download_url")

                        if download_url:
                            response = requests.get(download_url)

                            if response.status_code == 200:
                                status_text.text(f"Descargando informe para el ticker {ticker}...")
                                destino = os.path.join(ruta_descarga, f"{ticker}.xlsx")

                                with open(destino, "wb") as file:
                                    file.write(response.content)

                                progress = i / len(selected_tickers)
                                progress_bar.progress(progress)
                                descargas_exitosas += 1
                                tickers_descargados.append(ticker)
                            else:
                                status_text.text(f"Error al descargar informe para el ticker {ticker}!")
                    else: 
                        status_text.text(f"Informe no encontrado para {ticker}!")

                if descargas_exitosas  > 0:
                    descargados_text = ", ".join(tickers_descargados)
                    mensaje = f"{descargas_exitosas} de {total_tickers} tickers descargados en {ruta_descarga}: {descargados_text} "
                    status_text.text(mensaje)
                else:
                    status_text.text("No se encontraron informes para los tickers seleccionados.")                      
            else:
                st.write("No se han seleccionado tickers")    
    else:
        st.write("No tickers found for the selected industry")
else:
    st.write("No industry selected")
