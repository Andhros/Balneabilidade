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
    size='e_coli', color='e_coli', mapbox_style='carto-positron', center={"lat": -27.61587, "lon": -48.48378}, zoom=8)

# groups the data by point and takes the e coli mean for  each year of the historical series of each point
e_coli_ponto_year = df.groupby(['ponto', df.dateTime.dt.year, 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura', 
                                'lat', 'long'], as_index=True)['e_coli'].mean().reset_index()

 