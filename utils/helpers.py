# import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# # GDP_df
# def real_gdp_df():
#     GDP_df = pd.read_csv('data/A191RL1Q225SBEA.csv')
#     GDP_df['DATE'] = pd.to_datetime(GDP_df['DATE'])
#     GDP_df.set_index('DATE', inplace=True)
#     GDP_df.columns = ['GDP']
#     return GDP_df