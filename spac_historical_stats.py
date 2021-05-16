"""
	Description:
		Helper functions for historical stats analysis
"""


import numpy as np
import pandas as pd
import plotly.graph_objs as go


COLUMNS_CHG = ['open_close_t+1_%chg', 'open_close_t+3_%chg', 'open_close_t+5_%chg', 'open_close_t+7_%chg',
			   'open_close_t+10_%chg', 'open_close_t+12_%chg', 'open_completion_%chg']


def plot_cumulative_return(df, symbolType):
	df.sort_values(by='date', inplace=True)
	df_cumsum = df.set_index('date')[COLUMNS_CHG].cumsum()
	min_date = df_cumsum[~df_cumsum['open_close_t+1_%chg'].isna()].index.min()
	df_cumsum = df_cumsum[df_cumsum.index>=min_date]
	fig = go.Figure()
	fig.update_layout(title='Cumulative Return Trading on All Form 8-Ks: SPAC {}'.format(symbolType),
	                  xaxis_title='Date',
	                  yaxis_title='Cumulative Return in Percentage Points (10 = 1000%)')
	for column_chg in COLUMNS_CHG:
	    fig.add_trace(go.Scatter(x=df_cumsum.index,
	                             y=df_cumsum[column_chg],
	                             mode='lines+markers',
	                             marker=dict(size=3),
	                             name=column_chg))
	return fig


def compute_mean_returns(df_returns, corrupt_symbols):
    agg_dict = {'open_close_t+1_%chg':'mean','open_close_t+3_%chg':'mean',
                'open_close_t+5_%chg':'mean','open_close_t+7_%chg':'mean',
                'open_close_t+10_%chg':'mean','open_close_t+12_%chg':'mean',
                'open_completion_%chg':'mean'}
    df_mean_returns = df_returns[~df_returns.symbol.isin(corrupt_symbols)].groupby('symbol').agg(agg_dict)
    if len(corrupt_symbols)!=0:
        print('Symbols removed:', corrupt_symbols)
    df_mean_returns.dropna(subset=[x for x in COLUMNS_CHG if x != 'open_completion_%chg'], inplace=True)
    return np.round(df_mean_returns, 3)


def compute_summary_statistics(df_returns, corrupt_symbols):
    if len(corrupt_symbols)!=0:
        print('Symbols removed:', corrupt_symbols)
    df_returns.dropna(subset=[x for x in COLUMNS_CHG if x != 'open_completion_%chg'], inplace=True)
    return np.round(df_returns[~df_returns.symbol.isin(corrupt_symbols)][COLUMNS_CHG].describe(), 3)

