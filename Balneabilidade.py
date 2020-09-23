import numpy as np
import time
import pandas as pd
import requests
import json
import functools
import operator

# requests urls
url_municipios = 'https://balneabilidade.ima.sc.gov.br/municipio/getMunicipios'
url_locais = 'https://balneabilidade.ima.sc.gov.br/local/getLocaisByMunicipio'
url_anos = 'https://balneabilidade.ima.sc.gov.br/registro/anosAnalisados'
url_dados = 'https://balneabilidade.ima.sc.gov.br/relatorio/historico'

url_list =[url_municipios, url_locais, url_anos, url_dados]

# extract the list of years -> used to do one request per year
anos = json.loads(requests.get(url_anos).text)
anos = [i['ANO'] for i in anos]

# makes one request per year (using url_dados) 
# all the monitoring points ('localID' : 0) in Florianopólis city ('municipioID' : 2)
print('Request Loop Started')
ti = time.time()
list_req = [requests.post(url_dados,
                          data={
                              "municipioID": 2,
                              "localID": 0,
                              "ano": i,
                              "redirect": True
                          }) for i in anos]
tf = time.time()
print([i.status_code == 200 for i in list_req])
print()
print('Request Loop Finished in',tf-ti, 'seconds')

# creates empty lists to store the dataframes 
# 'lugares' -> details of locations of the monitorint points / 'dados' -> data of interest
lugares = []
dados = []


print()
print('For Loop Started')
ti2 = time.time()

# iterates over the results returned for each year
for i in list_req: 

    # reads the html and puts the tables in dataframes
    rawdata = pd.read_html(i.text)

    # the first dataframe for each year has no use
    rawdata.pop(0)

    # the dataframes alternate between location details and monitoring data
    # subsets the result for dataframes with location details 
    infodf = rawdata[0:(len(rawdata)+1):2]

    # subsets the result for dataframes with the monitoring data
    listdf = rawdata[1:(len(rawdata)+1):2]

    # extracts and wrangle the details of the location into the correct dataframe format
    infodf_new = []
    for i, j in zip (infodf, listdf):
        # for the info df, attain the point number:
        j['ponto'] = i.iloc[1, 0].lower().strip('ponto de coleta: ponto ')
        
        # transform every info df column-wise
        infodf_added = pd.DataFrame(
                    {'municipio': i.iloc[0,0].lower().replace('município: ', ''),
                    'balneario': i.iloc[0,1].lower().replace('balneário: ', ''),
                    'ponto': i.iloc[1,0].lower().replace('ponto de coleta: ponto ', ''),
                    'localizacao': i.iloc[1,1].lower().replace('localização: ', '')}, index=[0]
                )
        # create appended list of df
        infodf_new.append(infodf_added)

    # creates one dataframe with the location details of all points monitored in a year
    locais = pd.concat(infodf_new)
    locais.reset_index(drop=True, inplace=True)

    # crates one dataframe with the data from all the points monitored in a year 
    df = pd.concat(listdf)
    df.reset_index(drop=True, inplace=True)

    # append to the corresponding list of dataframes
    lugares.append(locais)
    dados.append(df)
tf2 = time.time()
print()
print('For Loop Finished in', tf2-ti2, 'seconds')

# concats the data frames for each year into a single df (location details)
spots = pd.concat(lugares).reset_index(drop=True)
spots = spots.drop_duplicates(subset='ponto', keep='first').reset_index(drop=True)

# concats the data frames for each year into a single df (monitoring data)
df = pd.concat(dados).reset_index(drop=True)

# there are a lot of missing values in the 'hour' column
# this subsets the df into rows that 'hour is not null'
# the objective is to get a 'mean' hour to fill the na values later
mean_hour = df[df['Hora'].notnull()]

# sets up a moderate value into a row that contained an impossible value ('92:...')
mean_hour.iloc[7077, 1] = '08:30:00'

# transforms the column into datetime
mean_hour['Hora'] = pd.to_datetime(mean_hour['Hora'])

# function to get the 'mean' hour
def avg_datetime(series):
    dt_min = series.min()
    deltas = [x-dt_min for x in series]
    return dt_min + functools.reduce(operator.add, deltas) / len(deltas)

# executes function to get the mean hour    
mean_h = avg_datetime(mean_hour['Hora'])

# fill the na values with the 'mean' hour
df['Hora'].fillna('09:41:46', inplace=True)

df.iloc[7077, 1] = '09:41:46'

# gets the date and hour columns and defines a datetime column
df['dateTime'] = pd.to_datetime(df.Data + ' ' + df.Hora)

# drops the old date and hour columns
df.drop(columns=['Data', 'Hora'], inplace=True)

# the columns with air and wates temperatures contain symbols that need to be removed
# removes the symbols and tranforms the columns into type float
def transform_colT(coluna):
    df[coluna] = df[coluna].apply(lambda x: x.replace(' Cº', ''))
    df[coluna] = df[coluna].apply(lambda x: x.replace('Cº', ''))
    df[coluna] = df[coluna].apply(lambda x: np.nan if isinstance(x, str) and (x.isspace() or not x) else x)
    df[coluna] = df[coluna].astype('float')


# converts the rest of the columns to the right types
df['ponto'] = df['ponto'].astype('int')
df['Condição'] = df['Condição'].astype('category')
df['Vento'] = df['Vento'].astype('category')
df['Maré'] = df['Maré'].astype('category')
df['Chuva'] = df['Chuva'].astype('category')

# Reorder columns
cols = ['dateTime', 'ponto', 'Vento', 'Maré', 'Chuva', coluna, 'Ar (Cº)', 'E.Coli NMP*/100ml', 'Condição']
df = df[cols]

# some features of each point of monitoring were gathered manually
# this loads this features into a df
features_pontos = pd.read_excel('features_pontos.xlsx')

# adds the corresponding features to each point of monitoring
df = df.merge(features_pontos, left_on='ponto', right_on='id')

# drops the repetitive column
df.drop(columns=['id'], inplace=True)

df.to_csv('df.csv', sep=';')
