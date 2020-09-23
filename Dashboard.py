import pandas as pd
import numpy as np
import seaborn as sns

df = pd.read_csv('df.csv', sep=';').iloc[:, 1:]
