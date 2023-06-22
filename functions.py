import random
import pandas as pd
import requests
import csv
import os
from sec_api import QueryApi

# Lista de API_KEYs disponibles
API_KEYS = ['63274835ecc5a1f981da195d9fd28262ab6cd8c8aaefe5e673789e141d3a1217',
            'd4649215c7e1aaecc674f8e3e45c5c475abd123b1685101dd28e1e87c3dfc54a']
    #'94ddebe4c15a5191150a7b1e8016c60bb9be3bb56765e36a91afa85fc97347ee']
    #'56671d54ba2e2979e87efa21830ae0d3d89eb319677cce50ab62f124e2019c03']
    #'26d15175efbe120b02bccff9d1c6f3745169c057090e1409972a1a6f68a7b8a8']
            #,'054225985d07ac95a0662c9a230fec95898a79b11feb3e28249c6d09501cd4ea']
           # ,'e1e9d715b7238dc072bc17c7aed6a369179471d4cf09e2cd84d94869f940847b']

folder_path = './reports'

def random_key(keys = API_KEYS):
    """
    Genera una clave API aleatoria y devuelve una instancia de QueryApi.
    Parameters:
        keys (list): Una lista de claves API disponibles. Por defecto, se utiliza la variable API_KEYS.
    Returns:
        tuple: Una tupla que contiene la clave API aleatoria y una instancia de QueryApi.
    """
    API_KEY = random.choice(keys)
    queryApi = QueryApi(api_key=API_KEY)
    return API_KEY, queryApi

API_KEY, queryApi = random_key() 

def my_function(tickers):
    """
    Genera una consulta de ticker a partir de una lista de tickers.
    Parameters:
        tickers (list): Lista de tickers para incluir en la consulta.
    Returns:
        str: Consulta generada en formato de cadena de caracteres.
    Example:
        tickers = ['MSFT', 'TSLA', 'AAPL']
        query = my_function(tickers)
        # query = "ticker:(MSFT, TSLA, AAPL)"
    """
    ticker_query = "ticker:(" + ", ".join(tickers) + ")"
    return ticker_query


def get_filings(query):
    """
    Realiza consultas a la API de SEC para obtener informes financieros según los parámetros 
    de consulta proporcionados.

    Parámetros:
    - query (dict): Un diccionario que contiene los parámetros de consulta para la API de SEC.

    Retorna:
    - pandas.DataFrame: Un DataFrame que contiene los informes financieros normalizados obtenidos de la API de SEC.

    Descripción:
    Esta función realiza consultas a la API de SEC utilizando los parámetros de consulta especificados en el diccionario `query`.
    Itera sobre los resultados paginados de la consulta y almacena los informes financieros en una lista.
    Luego, utiliza la función `pd.json_normalize` para convertir la lista de informes financieros en un DataFrame.

    Ejemplo de uso:
    query = {
        "query": {
            "query_string": {
                "query": "formType:(\"10-K\") AND ticker:(MSFT, TSLA)"
            }
        },
        "from": "0",
        "size": "200",
        "sort": [{
            "filedAt": {
                "order": "desc"
            }
        }]
    }
    filings = get_filings(query)
    """
    API_KEY, queryApi = random_key() 
    from_param = 0
    size_param = 200
    all_filings = []

    while True:
        query['from'] = from_param
        query['size'] = size_param

        response = queryApi.get_filings(query)
        filings = response['filings']

        if len(filings) == 0:
            break

        all_filings.extend(filings)

        from_param += size_param

    return pd.json_normalize(all_filings)


def download_report(row):
    '''
    Descarga un informe financiero desde una URL y lo guarda en la ruta de destino especificada.

    Parameters:
        row (pd.Series): Fila del DataFrame que contiene los datos del informe financiero.

    Returns:
        None
    '''
    API_KEY, queryApi = random_key()
    base_url = 'https://archive.sec-api.io/'
    render_api_url = base_url + row['financialReportsUrl'] + '?token=' + API_KEY
    
    response = requests.get(render_api_url)
    
    file_name = f"{row['ticker']}-{row['periodOfReport']}-{row['formType']}.xlsx"
    file_path = f"{folder_path}/{file_name}"

    output = open(file_path, 'wb')
    output.write(response.content)
    output.close()



def get_tickers_by_industry(industry_code):
    """
    Obtiene una lista de tickers de la SEC según el nombre de industria especificado.

    Parámetros:
        - industry_code (str): El código de la industria para buscar los tickers.

    Retorna:
        - list or None: Una lista de diccionarios con la información de los tickers encontrados,
                        donde cada diccionario contiene los campos 'name', 'ticker', 'cik',
                        'sector', 'industry' y 'sic'. Si no se encontraron tickers o hubo un error
                        en la solicitud, se retorna None.

    Ejemplo de uso:
        industry_code = 'Information Technology Services'
        tickers = get_tickers_by_industry(industry_code)

        if tickers:
            for ticker in tickers:
                print("Name:", ticker['name'])
                print("Ticker:", ticker['ticker'])
                print("CIK:", ticker['cik'])
                print("Sector:", ticker['sector'])
                print("Industry:", ticker['industry'])
                print("SIC:", ticker['sic'])
                print("-----------------------------")
        else:
            print("No se encontraron tickers para la industria:", industry_code)
    """
    API_KEY, queryApi = random_key() 
    base_url = "https://api.sec-api.io/mapping/industry/"
    url = base_url + industry_code + '?token=' + API_KEY

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            tickers = []
            for item in data:
                ticker_info = {
                    'name': item['name'],
                    'ticker': item['ticker'],
                    'cik': item['cik'],
                    'sector': item['sector'],
                    'industry': item['industry'],
                    'sic': item['sic']
                }
                tickers.append(ticker_info)
            return tickers
        else:
            print("La respuesta está vacía. No se encontraron tickers.")
            return None
    else:
        print("Error en la solicitud:", response.status_code)
        return None


file_path='industry_list.csv'

def read_industry_list(file_path):
    """
    Lee un archivo CSV con una columna llamada "Industry" y devuelve una lista
    con los elementos de esa columna.

    Parámetros:
        - file_path (str): La ruta del archivo CSV a leer.

    Retorna:
        - list: Una lista con los elementos de la columna "Industry" del archivo CSV.

    Ejemplo de uso:
        industry_list = read_industry_list('industry_list.csv')
        print(industry_list)
    """
    industry_list = []
    
    try:
        with open(file_path, 'r', newline='') as file:
            lines = file.readlines()
            # Ignorar el encabezado
            for line in lines[1:]:
                industry = line.strip()
                if industry:
                    industry_list.append(industry)
    except FileNotFoundError:
        print("El archivo no fue encontrado:", file_path)
    except Exception as e:
        print("Ocurrió un error al leer el archivo:", str(e))

    return industry_list