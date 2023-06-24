import streamlit as st
from sec_api import QueryApi
import functions
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
        # Obtener la ruta absoluta del archivo de script actual
        current_path = os.path.abspath(__file__)

        # Construir la ruta relativa al directorio de informes
        folder_path = os.path.join(os.path.dirname(current_path), "reports/01-01-2022 al 31-12-2022")

        if st.button("Descargar informes"):
            if selected_tickers:
                progress_bar = st.progress(0)  # Barra de progreso inicializada en 0
                status_text = st.empty()  # Espacio para el texto de estado
                
                for i, ticker_info in enumerate(selected_tickers, 1):
                    ticker = ticker_info.split('-')[0].strip()
                    file_path = os.path.join(folder_path, f"{ticker}.xlsx")
                    
                    if os.path.isfile(file_path):
                        # Descargar el archivo
                        status_text.text(f"Descargando informe para el ticker {ticker}...")
                        # Aquí puedes agregar el código para descargar el archivo a tu sistema local
                        
                        # Actualizar la barra de progreso
                        progress = i / len(selected_tickers)
                        progress_bar.progress(progress)
                        
                # Mostrar el mensaje de descarga finalizada
                status_text.text(f"Descarga finalizada!\nArchivos descargados en: {folder_path}")
            else:
                st.write("No se han seleccionado tickers")

            
    else:
        st.write("No tickers found for the selected industry")
else:
    st.write("No industry selected")
