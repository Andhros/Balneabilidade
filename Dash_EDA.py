import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.figure_factory as ff

# reads the csv and parses the dateTime column
df = pd.read_csv('df.csv', sep=';', index_col=0, parse_dates=['dateTime'])

# renames the columns for better manipulation of the dataframe
df.rename(columns={'Vento': 'vento', 'Maré': 'mare', 'Chuva': 'chuva', 
                   'Agua (Cº)': 'temp_agua', 'Ar (Cº)': 'temp_ar', 'E.Coli NMP*/100ml': 'e_coli', 'Condição': 'condicao'}, inplace=True)

features_pontos = pd.read_excel('features_pontos.xlsx')

mapa = px.scatter_mapbox(
    features_pontos, lat='lat', lon='long', hover_data=['id', 'nome', 'referencia', 'localizacao', 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura'], 
    mapbox_style='carto-positron', center={"lat": -27.61587, "lon": -48.48378}, zoom=8)

years = list(df.dateTime.dt.year.unique())
years.append('Todos os anos')
pontos = list(df.ponto.sort_values().unique())
stats_list = ['Descrição sumarizada dos dados (df.describe())', 'Estatísticas de E. Coli por ponto', 
              'Condição de Balneabilidade por ponto', 'Estatísticas de E. Coli com relação à pluviosidade', 
              'Estatísticas de E. Coli por praias e pontos com desembocadura', 'Estatísticas de E. Coli por ano',
              'Estatísticas de E. Coli por mês']

#-----------------------------------------------------------------------------
### Summary Stats

describe = df.describe().reset_index()

summary_stats_ponto = df.groupby('ponto').agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
summary_stats_ponto.columns = summary_stats_ponto.columns.droplevel()

cross_condit = pd.crosstab(df.ponto, df.condicao, margins=True, margins_name='Total de medições').reset_index()
cross_condit['Porcentagem Imprópria'] = cross_condit['IMPRÓPRIA'] / cross_condit['Total de medições'] * 100
cross_condit['Porcentagem Própria'] = cross_condit['PRÓPRIA'] / cross_condit['Total de medições'] * 100
cross_condit['Porcentagem Indeterminado'] = cross_condit['INDETERMINADO'] / cross_condit['Total de medições'] * 100
cross_condit

summary_stats_chuva = df.groupby('chuva')['e_coli'].agg(['mean', 'median', 'var', 'std']).reset_index()

summary_stats_desemb = df.groupby(['agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura'])['e_coli'].agg(['mean', 'median', 'var', 'std']).reset_index()

summary_stats_year = df.groupby(df.dateTime.dt.year).agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
summary_stats_year.columns = summary_stats_year.columns.droplevel()

summary_stats_month = df.groupby(df.dateTime.dt.month).agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
summary_stats_month.columns = summary_stats_month.columns.droplevel()

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
                id='drop_years1',
                options=[{'label': i, 'value': i} for i in years],
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
                id='drop_years2',
                options=[{'label': i, 'value': i} for i in years],
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
            id='drop_stats',
            options=[{'label': i, 'value': i} for i in stats_list],
        ),
        dash_table.DataTable(
            id='table',
            page_size=10,
            data=[],
            ),
    ]),

])

@app.callback(
    [dash.dependencies.Output('graph1', 'figure'),
    dash.dependencies.Output('graph3', 'figure'),
    dash.dependencies.Output('graph5', 'figure'),
    dash.dependencies.Output('graph7', 'figure')],
    [dash.dependencies.Input('drop_ponto1', 'value'),
    dash.dependencies.Input('drop_years1', 'value')]
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
    dash.dependencies.Input('drop_years2', 'value')]
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
    [dash.dependencies.Input('drop_stats', 'value')],
)

def update_stats_table(df):
    
    if df is None:
        columns = []
        data = []
    
    elif df == 'Descrição sumarizada dos dados (df.describe())':
        table = describe
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Estatísticas de E. Coli por ponto':
        table = summary_stats_ponto
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
        
    elif df == 'Condição de Balneabilidade por ponto':
        table = cross_condit
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
        
    elif df == 'Estatísticas de E. Coli com relação à pluviosidade':
        table = summary_stats_chuva
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Estatísticas de E. Coli por praias e pontos com desembocadura':
        table = summary_stats_desemb
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Estatísticas de E. Coli por ano':
        table = summary_stats_year
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Estatísticas de E. Coli por mês':
        table = summary_stats_month
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    return data, columns


if __name__ == '__main__':
    app.run_server(debug=True)