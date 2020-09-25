import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px

# reads the csv and parses the dateTime column
df = pd.read_csv('df.csv', sep=';', index_col=0, parse_dates=['dateTime'])

# renames the columns for better manipulation of the dataframe
df.rename(columns={'Vento': 'vento', 'Maré': 'mare', 'Chuva': 'chuva', 
                   'Agua (Cº)': 'temp_agua', 'Ar (Cº)': 'temp_ar', 'E.Coli NMP*/100ml': 'e_coli'}, inplace=True)

# groups the data by point and takes the e coli mean for the historical series of each point
e_coli_ponto = df.groupby(['ponto', 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura', 
                           'lat', 'long'], as_index=False)['e_coli'].mean()

# creates a map with the mean of e coli per point
mapa_media_ponto = px.scatter_mapbox(
    e_coli_ponto, lat='lat', lon='long', hover_data=['ponto', 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura'], 
    size='e_coli', color='e_coli', mapbox_style='carto-positron', center={"lat": -27.61587, "lon": -48.48378}, zoom=9)

# groups the data by point and takes the e coli mean for  each year of the historical series of each point
e_coli_ponto_year = df.groupby(['ponto', df.dateTime.dt.year, 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura', 
                                'lat', 'long'], as_index=True)['e_coli'].mean().reset_index()

lineplot = px.scatter(e_coli_ponto, x='dateTime', y='e_coli', hover_data=['ponto'], color='ponto')

years = df.dateTime.dt.year.unique()
pontos = df.ponto.unique()

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
        )
    ]),
    
    html.Div([
        html.Div([
            dcc.Markdown('''#### Selecione o ano:'''),
            dcc.Dropdown(
                id='drop_year',
                options=[{'label': i, 'value': i} for i in years],
                value='Todos os anos'
            ),
        ], className='one-third column'),
        html.Div([
            dcc.Graph(
            id='mapa',
            figure=mapa_media_ponto
            )   
        ], className='two-thirds column'),
    ], className='row'),
    
    html.Div([
        dcc.Graph(
            id='mapa_pontos',
            figure=mapa_media_ponto
        )
    ])

])

if __name__ == '__main__':
    app.run_server(debug=True)
