import numpy as np
import time
import pandas as pd
import requests
import json
import functools
import operator

# urls de resquest
url_municipios = 'https://balneabilidade.ima.sc.gov.br/municipio/getMunicipios'
url_locais = 'https://balneabilidade.ima.sc.gov.br/local/getLocaisByMunicipio'
url_anos = 'https://balneabilidade.ima.sc.gov.br/registro/anosAnalisados'
url_dados = 'https://balneabilidade.ima.sc.gov.br/relatorio/historico'

url_lista =[url_municipios, url_locais, url_anos, url_dados]

# extrai a lista de anos
anos = json.loads(requests.get(url_anos).text)
anos = [i['ANO'] for i in anos]

# faz um resquest por ano 
# todos os pontos de monitoramento ('localID' : 0) em Florianópolis ('municipioID' : 2)
print('Loop de requests iniciado')
ti = time.time()
lista_rqs = [requests.post(url_dados,
                          data={
                              "municipioID": 2,
                              "localID": 0,
                              "ano": i,
                              "redirect": True
                          }) for i in anos]
tf = time.time()
print([i.status_code == 200 for i in lista_rqs])
print()
print('Loop de requests finalizado',tf-ti, 'segundos')

# cria listas vazias para armazenar os dataframes
# 'lugares' -> detalhes de localização dos pontos / 'dados' -> dados de interesse
lugares = []
dados = []


print()
print('For loop iniciado')
ti2 = time.time()

# iterates sobre os resultados de cada ano
for i in lista_rqs: 

    # lê o html e coloca as tabelas em dataframes
    dados_brutos = pd.read_html(i.text)

    # o primeiro dataframe para cada ano não tem utilidade (é somente um cabeçalho)
    dados_brutos.pop(0)

    # os dataframes se alternam entre os detalhes de localização e os dados do ponto
    # seleciona os dataframes com detalhes de localização dos pontos 
    infodf = dados_brutos[0:(len(dados_brutos)+1):2]

    # seleciona os dataframes com dados de interesse dos pontos
    listadf = dados_brutos[1:(len(dados_brutos)+1):2]

    # extraí e compila os detalhes de localização em um dataframe organizado
    infodf_new = []
    for i, j in zip (infodf, listadf):
        # for the info df, attain the point number:
        j['ponto'] = i.iloc[1, 0].lower().strip('ponto de coleta: ponto ')
        
        # transformação de colunas
        infodf_adic = pd.DataFrame(
                    {'municipio': i.iloc[0,0].lower().replace('município: ', ''),
                    'balneario': i.iloc[0,1].lower().replace('balneário: ', ''),
                    'ponto': i.iloc[1,0].lower().replace('ponto de coleta: ponto ', ''),
                    'localizacao': i.iloc[1,1].lower().replace('localização: ', '')}, index=[0]
                )
        # adiciona o df e adiciona a lista info novo df
        infodf_new.append(infodf_adic)

    # cria um dataframe com os detalhes de localização de todos pontos monitorados
    locais = pd.concat(infodf_new)
    locais.reset_index(drop=True, inplace=True)

    # cria um dataframe com os dados de interesse de todos os pontos monitorados 
    df = pd.concat(listadf)
    df.reset_index(drop=True, inplace=True)

    # adiciona os dataframes as listas correspondentes
    lugares.append(locais)
    dados.append(df)
tf2 = time.time()
print()
print('For Loop finalizado', tf2-ti2, 'segundos')

# concatena os dataframes de cada ano em um único df (detalhes de localização)
localiz = pd.concat(lugares).reset_index(drop=True)
localiz = localiz.drop_duplicates(subset='ponto', keep='first').reset_index(drop=True)

# concatena os dataframes de cada ano em um único df (dados de interesse)
df = pd.concat(dados).reset_index(drop=True)

# existem muitos valores faltantes na coluna de hora
# preenche os valores faltantes com uma hora "razoável", uma vez que as amostras são coletadas pela manhã
df['Hora'].fillna('09:30:00', inplace=True)

# substituí uma célula onde a hora tem um valor impossível('92:07:00')
df.loc[df['Hora'] == '92:07:00', ['Hora']] = '09:30:00'

# pega as colunas de data e hora e cria uma coluna de dateTime
df['dateTime'] = pd.to_datetime(df.Data + ' ' + df.Hora)

# remove as colunas de data e hora
df.drop(columns=['Data', 'Hora'], inplace=True)

# as colunas de temperatura da água e do ar contém símbolos que necessitam ser removidos
# remove os símbolos e transforma as colunas para tipo float
def transform_colT(coluna):
    df[coluna] = df[coluna].apply(lambda x: x.replace(' Cº', ''))
    df[coluna] = df[coluna].apply(lambda x: x.replace('Cº', ''))
    df[coluna] = df[coluna].apply(lambda x: np.nan if isinstance(x, str) and (x.isspace() or not x) else x)
    df[coluna] = df[coluna].astype('float')
    return df[coluna]

df['Agua (Cº)'] = transform_colT('Agua (Cº)')
df['Ar (Cº)'] = transform_colT('Ar (Cº)')

# converte o resto das colunas para os tipos corretos de dados
df['ponto'] = df['ponto'].astype('int')
df['Condição'] = df['Condição'].astype('category')
df['Vento'] = df['Vento'].astype('category')
df['Maré'] = df['Maré'].astype('category')
df['Chuva'] = df['Chuva'].astype('category')

# reordena as colunas
cols = ['dateTime', 'ponto', 'Vento', 'Maré', 'Chuva', 'Agua (Cº)', 'Ar (Cº)', 'E.Coli NMP*/100ml', 'Condição']
df = df[cols]

# renomeia as colunas para facilitar manipulação
df.rename(columns={'Vento': 'vento', 'Maré': 'mare', 'Chuva': 'chuva', 
                   'Agua (Cº)': 'temp_agua', 'Ar (Cº)': 'temp_ar', 'E.Coli NMP*/100ml': 'e_coli', 'Condição': 'condicao'}, inplace=True)

# tabela contendo os atributos coletados de forma manual
atributos_pontos = pd.read_excel('atributos_pontos.xlsx')

# adiciona os atributos correspondentes fazendo a junção dos dois dataframes
df = df.merge(atributos_pontos, left_on='ponto', right_on='ponto')

df.to_csv('df.csv', sep=';')
