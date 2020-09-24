import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px

df = pd.read_csv('df.csv', sep=';', index_col=0)

df.rename(columns={'Vento': 'vento', 'Maré': 'mare', 'Chuva': 'chuva', 'Agua (Cº)': 'temp_agua', 'Ar (Cº)': 'temp_ar', 'E.Coli NMP*/100ml': 'e_coli'}, inplace=True)

e_coli_ponto = df.groupby(['ponto', 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura', 'lat', 'long'], as_index=False)['e_coli'].mean()

mapa_media_ponto = px.scatter_mapbox(e_coli_ponto, lat='lat', lon='long', size='e_coli', color='e_coli', mapbox_style='carto-positron', center={"lat": -27.61587, "lon": -48.48378}, zoom=8)

