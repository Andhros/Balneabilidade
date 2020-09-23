import pandas as pd
import numpy as np
import seaborn as sns

df = pd.read_csv('df.csv', sep=';', index_col=0)

e_coli_ponto = df.groupby(['ponto', 'agua_doce', 'desembocadura_praia', 'ponto_perto_desembocadura', 'lat', 'long'], as_index=False)['E.Coli NMP*/100ml'].mean()
