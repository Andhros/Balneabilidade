import numpy as np
import pandas as pd
import requests
import json

url_municipios = 'https://balneabilidade.ima.sc.gov.br/municipio/getMunicipios'
url_locais = 'https://balneabilidade.ima.sc.gov.br/local/getLocaisByMunicipio'
url_anos = 'https://balneabilidade.ima.sc.gov.br/registro/anosAnalisados'

url_list =[url_municipios, url_locais, url_anos]

var = pd.read_html(requests.post('https://balneabilidade.ima.sc.gov.br/relatorio/historico', 
                           data={
    "municipioID": 2,
    "localID": 0,
    "ano": 2014,
    "redirect": True
}).text)

# for i in url_list


