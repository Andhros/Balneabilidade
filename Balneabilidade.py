import numpy as np
import time
import pandas as pd
import requests
import json
import functools
import operator


url_municipios = 'https://balneabilidade.ima.sc.gov.br/municipio/getMunicipios'
url_locais = 'https://balneabilidade.ima.sc.gov.br/local/getLocaisByMunicipio'
url_anos = 'https://balneabilidade.ima.sc.gov.br/registro/anosAnalisados'
url_dados = 'https://balneabilidade.ima.sc.gov.br/relatorio/historico'

url_list =[url_municipios, url_locais, url_anos, url_dados]

anos = json.loads(requests.get(url_anos).text)
anos = [i['ANO'] for i in anos]

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


lugares = []
dados = []


print()
print('For Loop Started')
ti2 = time.time()
for i in list_req: 

    rawdata = pd.read_html(i.text)

    rawdata.pop(0)

    infodf = rawdata[0:(len(rawdata)+1):2]

    listdf = rawdata[1:(len(rawdata)+1):2]

    infodf_new = []
    for i, j in zip (infodf, listdf):
        # for the info df, attain point number:
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

    locais = pd.concat(infodf_new)
    locais.reset_index(drop=True, inplace=True)

    df = pd.concat(listdf)
    df.reset_index(drop=True, inplace=True)

    lugares.append(locais)
    dados.append(df)
tf2 = time.time()
print()
print('For Loop Finished in', tf2-ti2, 'seconds')

spots = pd.concat(lugares).reset_index(drop=True)
spots = spots.drop_duplicates(subset='ponto', keep='first').reset_index(drop=True)

df = pd.concat(dados).reset_index(drop=True)

mean_hour = df[df['Hora'].notnull()]

mean_hour.iloc[7077, 1] = '08:30:00'

mean_hour['Hora'] = pd.to_datetime(mean_hour['Hora'])

def avg_datetime(series):
    dt_min = series.min()
    deltas = [x-dt_min for x in series]
    return dt_min + functools.reduce(operator.add, deltas) / len(deltas)
    
mean_h = avg_datetime(mean_hour['Hora'])

df['Hora'].fillna('09:41:46', inplace=True)

df.iloc[7077, 1] = '09:41:46'

df['dateTime'] = pd.to_datetime(df.Data + ' ' + df.Hora)

df.drop(columns=['Data', 'Hora'], inplace=True)

df['Agua (Cº)'].replace(' Cº', '')
df['Agua (Cº)'].replace('', np.nan)
df['Agua (Cº)'].astype('float')
