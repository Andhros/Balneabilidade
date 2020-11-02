import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.figure_factory as ff

# reads the csv and parses the dateTime column
df = pd.read_csv('df.csv', sep=';', index_col=0, parse_dates=['dateTime'])

# renames the columns for better manipulation of the dataframe
df.rename(columns={'Vento': 'vento', 'Maré': 'mare', 'Chuva': 'chuva', 
                   'Agua (Cº)': 'temp_agua', 'Ar (Cº)': 'temp_ar', 'E.Coli NMP*/100ml': 'e_coli'}, inplace=True)

features_pontos = pd.read_excel('features_pontos.xlsx')

mapa = px.scatter_mapbox(
    features_pontos, lat='lat', lon='long', hover_data=['id', 'nome', 'referencia', 'localizacao', 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura'], 
    mapbox_style='carto-positron', center={"lat": -27.61587, "lon": -48.48378}, zoom=8)

years = df.dateTime.dt.year.unique()
pontos = df.ponto.sort_values().unique()

#-----------------------------------------------------------------------------
### Dashboard

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

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
            dcc.Markdown('''###### Selecione um ponto'''), 
            dcc.Dropdown(
                id='drop_ponto1',
                options=[{'label': i, 'value': i} for i in pontos],
            ),
            dcc.Graph(id='graph1'),
            dcc.Graph(id='graph3'),
            dcc.Graph(id='graph5'),
            dcc.Graph(id='graph7')
        ], className='six columns'),
        html.Div([
            dcc.Markdown('''###### Selecione um ponto'''), 
            dcc.Dropdown(
                id='drop_ponto2',
                options=[{'label': i, 'value': i} for i in pontos],
            ),
            dcc.Graph(id='graph2'),
            dcc.Graph(id='graph4'),
            dcc.Graph(id='graph6'),
            dcc.Graph(id='graph8')
        ], className='six columns'),
    ]),

])

@app.callback(
    [dash.dependencies.Output('graph1', 'figure'),
    dash.dependencies.Output('graph3', 'figure'),
    dash.dependencies.Output('graph5', 'figure'),
    dash.dependencies.Output('graph7', 'figure')],
    [dash.dependencies.Input('drop_ponto1', 'value')]
)

def update_graph(pointN):
    filtered_df = df[df.ponto == pointN].sort_values(by='dateTime')
        
    graph1 = px.histogram(filtered_df, x="e_coli", marginal="rug",
                          histnorm='percent', range_x=[0, 25000], nbins=25)
    
    graph3 = px.box(filtered_df, y='e_coli')
        
    graph5 = px.line(filtered_df, x='dateTime', y='e_coli', hover_data=df.columns)
    
    group_chuva = filtered_df.groupby('chuva', as_index=False)['e_coli'].mean()
    
    graph7 = px.bar(data_frame=group_chuva, x='chuva', y='e_coli', color='chuva')
        
    return graph1, graph3, graph5, graph7

@app.callback(
    [dash.dependencies.Output('graph2', 'figure'),
    dash.dependencies.Output('graph4', 'figure'),
    dash.dependencies.Output('graph6', 'figure'),
    dash.dependencies.Output('graph8', 'figure')],
    [dash.dependencies.Input('drop_ponto2', 'value')]
)

def update_graph2(pointN2):
    filtered_df1 = df[df.ponto == pointN2].sort_values(by='dateTime')

    graph2 = px.histogram(filtered_df1, x="e_coli", marginal="rug",
                          histnorm='percent', range_x=[0, 25000], nbins=25)
    
    graph4 = px.box(filtered_df1, y='e_coli')
    
    graph6 = px.line(filtered_df1, x='dateTime', y='e_coli', hover_data=df.columns)

    group_chuva1 = filtered_df1.groupby('chuva', as_index=False)['e_coli'].mean()
    
    graph8 = px.bar(data_frame=group_chuva1, x='chuva', y='e_coli', color='chuva')

    return graph2, graph4, graph6, graph8

if __name__ == '__main__':
    app.run_server(debug=True)
