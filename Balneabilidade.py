import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import json

url_municipios = 'https://balneabilidade.ima.sc.gov.br/municipio/getMunicipios'
url_locais = 'https://balneabilidade.ima.sc.gov.br/local/getLocaisByMunicipio'
url_anos = 'https://balneabilidade.ima.sc.gov.br/registro/anosAnalisados'

url_list =[url_municipios, url_locais, url_anos]

pd.read_html(requests.post('https://balneabilidade.ima.sc.gov.br/relatorio/historico', 
                           data={
    "municipioID": 2,
    "localID": 0,
    "ano": 2014,
    "redirect": True
}).text)

# for i in url_list


# read html file for 1 year and make soup
with open('bal_2015.html', encoding='utf8') as file:
    soup = BeautifulSoup(file)

# extract all the tables from the html
tables = soup.find_all('table')

#iterates all the tables and gets the data
dfs_list_2015 = []
for table in tables:
    rows = table.find_all('tr')
    output = []
    for row in rows:
        cols = row.find_all(['td', 'th'])
        cols = [item.text.strip() if item.text.strip() !=
                '' else np.nan for item in cols]
        output.append([item for item in cols if item])

    df = pd.DataFrame(output, columns=output[0])
    df.drop(0, inplace=True)
    df.reset_index(drop=True, inplace=True)
    dfs_list_2015.append(df)

del dfs_list_2015[0]  # delete first dataframe (useless)

# gets the list of all the points
pontos_list = [i.iloc[0, 0] for i in dfs_list_2015[0:(len(dfs_list_2015)+1):2]]

#assign a column for each data frame with the point number
for index, df in enumerate(dfs_list_2015[1:(len(dfs_list_2015)+1):2]):
    df['ponto'] = pd.Series(
        [pontos_list[index].lower().strip('ponto de coleta: ponto ')] * len(df))


dfs_resumo_local_list = []
for df in dfs_list_2015[0:(len(dfs_list_2015)+1):2]:
    df = pd.DataFrame(
        {'municipio': df.columns[0].lower().strip('município: '),
         'balneario': df.columns[1].lower().strip('balneário: '),
         'ponto': df.iloc[0, 0].lower().strip('ponto de coleta: ponto '),
         'localizacao': df.iloc[0, 1].lower().strip('localização: ')}, index=[0]
    )

    dfs_resumo_local_list.append(df)

df_localizacao_pontos = pd.concat(dfs_resumo_local_list)

df_localizacao_pontos.reset_index(drop=True, inplace=True)

del dfs_list_2015[0:(len(dfs_list_2015)+1):2]

df_all_pontos_2015 = pd.concat(dfs_list_2015)

df_all_pontos_2015['Data'] = df_all_pontos_2015.Data.str.replace('/', '-')

df_all_pontos_2015['datetime'] = df_all_pontos_2015.Data.str.cat(
    df_all_pontos_2015.Hora, sep=' ')
