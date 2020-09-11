import numpy as np
import pandas as pd
import requests
import json

url_municipios = 'https://balneabilidade.ima.sc.gov.br/municipio/getMunicipios'
url_locais = 'https://balneabilidade.ima.sc.gov.br/local/getLocaisByMunicipio'
url_anos = 'https://balneabilidade.ima.sc.gov.br/registro/anosAnalisados'

url_list =[url_municipios, url_locais, url_anos]



    req = pd.read_html(requests.post('https://balneabilidade.ima.sc.gov.br/relatorio/historico', 
                            data={
        "municipioID": 2,
        "localID": 0,
        "ano": 2014,
        "redirect": True
    }).text)

    req.pop(0)

    infodf = req[0:(len(req)+1):2]

    listdf = req[1:(len(req)+1):2]

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

