import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff


# lê o csv e faz o parse da coluna dateTime
df = pd.read_csv('df.csv', sep=';', index_col=0, parse_dates=['dateTime'])

atributos_pontos = pd.read_excel('atributos_pontos.xlsx')

mapa = px.scatter_mapbox(
    atributos_pontos, lat='lat', lon='long', hover_data=['ponto', 'balneario', 'referencia', 'localizacao', 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura'], 
    mapbox_style='carto-positron', center={"lat": -27.61587, "lon": -48.48378}, zoom=8)

anos = list(df.dateTime.dt.year.unique())
anos.append('Todos os anos')
pontos = list(df.ponto.sort_values().unique())
estats_lista = ['Descrição sumarizada dos dados (df.describe())', 'Estatísticas de E. Coli por ponto', 
              'Condição de Balneabilidade por ponto', 'Estatísticas de E. Coli com relação à pluviosidade', 
              'Estatísticas de E. Coli por praias e pontos com desembocadura', 'Estatísticas de E. Coli por ano',
              'Estatísticas de E. Coli por mês']

#-----------------------------------------------------------------------------
### Tabelas estatísticas

descricao = df.describe().reset_index()

estats_ponto = df.groupby('ponto').agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
estats_ponto.columns = estats_ponto.columns.droplevel()

cross_condicao = pd.crosstab(df.ponto, df.condicao, margins=True, margins_name='Total de medições').reset_index()
cross_condicao['Porcentagem Imprópria'] = cross_condicao['IMPRÓPRIA'] / cross_condicao['Total de medições'] * 100
cross_condicao['Porcentagem Própria'] = cross_condicao['PRÓPRIA'] / cross_condicao['Total de medições'] * 100
cross_condicao['Porcentagem Indeterminado'] = cross_condicao['INDETERMINADO'] / cross_condicao['Total de medições'] * 100
cross_condicao

estats_chuva = df.groupby('chuva')['e_coli'].agg(['mean', 'median', 'var', 'std']).reset_index()

estats_desmb = df.groupby(['agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura'])['e_coli'].agg(['mean', 'median', 'var', 'std']).reset_index()

estats_anos = df.groupby(df.dateTime.dt.year).agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
estats_anos.columns = estats_anos.columns.droplevel()

estats_meses = df.groupby(df.dateTime.dt.month).agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
estats_meses.columns = estats_meses.columns.droplevel()

#-----------------------------------------------------------------------------
### Dashboard

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

app.layout = html.Div([
    html.Div([
        html.H1(
            children='Análise de balneabilidade | Florianópolis - SC',
            style={
                'textAlign' : 'center',
            }
        ),
        dcc.Graph(id='mapa1', figure=mapa)
    ]),
    
    html.Div([
        html.Div([
            dcc.Markdown('''###### Ponto de monitoramento'''), 
            dcc.Dropdown(
                id='drop_ponto1',
                options=[{'label': i, 'value': i} for i in pontos],
            ),
            dcc.Markdown('''###### Ano'''),
            dcc.Dropdown(
                id='drop_anos1',
                options=[{'label': i, 'value': i} for i in anos],
                value='Todos os anos'
            ),
            dcc.Graph(id='graph1'),
            dcc.Graph(id='graph3'),
            dcc.Graph(id='graph5'),
            dcc.Graph(id='graph7'),
        ], className='six columns'),
        html.Div([
            dcc.Markdown('''###### Ponto de monitoramento'''), 
            dcc.Dropdown(
                id='drop_ponto2',
                options=[{'label': i, 'value': i} for i in pontos],
            ),
            dcc.Markdown('''###### Ano'''),
            dcc.Dropdown(
                id='drop_anos2',
                options=[{'label': i, 'value': i} for i in anos],
                value='Todos os anos'
            ),
            dcc.Graph(id='graph2'),
            dcc.Graph(id='graph4'),
            dcc.Graph(id='graph6'),
            dcc.Graph(id='graph8'),
        ], className='six columns'),
    ]),
    
    html.Div([
        html.H4(
            children='Tabelas Estatísticas',
            style={
                'textAlign' : 'center',
            }
        ),
        dcc.Dropdown(
            id='drop_estats',
            options=[{'label': i, 'value': i} for i in estats_lista],
        ),
        dash_table.DataTable(
            id='table',
            page_size=10,
            data=[],
        ),
        html.H1(
            children='__________________________________________',
            style={
                'textAlign' : 'center',
            }
        ),
        html.H6(
            children='Dados retirados de: https://balneabilidade.ima.sc.gov.br/',
            style={
                'textAlign' : 'center',
            }
        ),
        html.H6(
            children='Criado por: Andhros Guimarães e David Guimarães',
            style={
                'textAlign' : 'center',
            }
        ),
        html.H1(
            children='-----------------------------------------',
            style={
                'textAlign' : 'center',
            }
        ),
    ]),

])

@app.callback(
    [dash.dependencies.Output('graph1', 'figure'),
    dash.dependencies.Output('graph3', 'figure'),
    dash.dependencies.Output('graph5', 'figure'),
    dash.dependencies.Output('graph7', 'figure')],
    [dash.dependencies.Input('drop_ponto1', 'value'),
    dash.dependencies.Input('drop_anos1', 'value')]
)

def update_graph(pointN, yearsN):
    
    if yearsN == 'Todos os anos':
        filtered_df = df[df.ponto == pointN].sort_values(by='dateTime')
    
    else:
        filtered_df = df[(df.ponto == pointN) & (df.dateTime.dt.year == yearsN)].sort_values(by='dateTime')
        
    graph1 = px.histogram(filtered_df, x="e_coli", marginal="rug",
                          histnorm='percent', range_x=[0, 25000], nbins=25, 
                          title='Histogram - Porcentagem de medições x valores de E. Coli')
    
    graph3 = px.violin(filtered_df, y='e_coli', title='Violin Plot - Distribuição de valores de E. Coli')
    
    graph5 = px.box(filtered_df, y='e_coli', title='Box plot - Distribuição de valores de E. Coli')
        
    graph7 = px.line(filtered_df, x='dateTime', y='e_coli', hover_data=df.columns,
                     title='Time Series - Valores de E. Coli')
    
    return graph1, graph3, graph5, graph7

@app.callback(
    [dash.dependencies.Output('graph2', 'figure'),
    dash.dependencies.Output('graph4', 'figure'),
    dash.dependencies.Output('graph6', 'figure'),
    dash.dependencies.Output('graph8', 'figure')],
    [dash.dependencies.Input('drop_ponto2', 'value'),
    dash.dependencies.Input('drop_anos2', 'value')]
)

def update_graph2(pointN2, yearsN2):
    if yearsN2 == 'Todos os anos':
        filtered_df1 = df[df.ponto == pointN2].sort_values(by='dateTime')
    
    else:
        filtered_df1 = df[(df.ponto == pointN2) & (df.dateTime.dt.year == yearsN2)].sort_values(by='dateTime')

    graph2 = px.histogram(filtered_df1, x="e_coli", marginal="rug",
                          histnorm='percent', range_x=[0, 25000], nbins=25,
                          title='Histogram - Porcentagem de medições x valores de E. Coli')
    
    graph4 = px.violin(filtered_df1, y='e_coli', title='Violin Plot - Distribuição de valores de E. Coli')
    
    graph6 = px.box(filtered_df1, y='e_coli', title='Box plot - Distribuição de valores de E. Coli')
    
    graph8 = px.line(filtered_df1, x='dateTime', y='e_coli', hover_data=df.columns,
                     title='Time Series - Valores de E. Coli')

    return graph2, graph4, graph6, graph8


@app.callback(
    [dash.dependencies.Output('table', 'data'),
     dash.dependencies.Output('table', 'columns')],
    [dash.dependencies.Input('drop_estats', 'value')],
)

def update_stats_table(df):
    
    if df is None:
        columns = []
        data = []
    
    elif df == 'Descrição sumarizada dos dados (df.describe())':
        table = descricao
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Estatísticas de E. Coli por ponto':
        table = estats_ponto
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
        
    elif df == 'Condição de Balneabilidade por ponto':
        table = cross_condicao
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
        
    elif df == 'Estatísticas de E. Coli com relação à pluviosidade':
        table = estats_chuva
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Estatísticas de E. Coli por praias e pontos com desembocadura':
        table = estats_desmb
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Estatísticas de E. Coli por ano':
        table = estats_anos
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Estatísticas de E. Coli por mês':
        table = estats_meses
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    return data, columns


if __name__ == '__main__':
    app.run_server(debug=True)