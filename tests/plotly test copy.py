import quantfreedom as qf
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from quantfreedom.backtester.indicators.talib_ind import from_talib
from quantfreedom._typing import (
    pdFrame, pdSeries
)
prices = pd.read_csv(
    'E:/Coding/backtesters/QuantFreedom/tests/30min.csv', index_col='time')
rsi_ind = from_talib(
    func_name='rsi',
    df_prices=prices,
    cart_product=False,
    combos=False,
    timeperiod=[15, 55],
)
df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')


temp_list = []
for count, value in enumerate(list(rsi_ind.columns)):
    temp_list.append(value[0])
    
# dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
# app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
app = Dash(__name__)

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

fig = go.Figure()

candle_fig = go.Figure(
    data=[
        go.Candlestick(
            x=prices.index,
            open=prices.open,
            high=prices.high,
            low=prices.low,
            close=prices.close,
            name='Candles'
        ),
    ],
    layout_xaxis_rangeslider_visible=False,
)

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('ind-settings', 'value'),
)
def update_figure(selected_ind_settings):
    fig = px.line(
        x=rsi_ind.index.to_list(),
        y=rsi_ind[selected_ind_settings].values.flatten(),
    )

    fig.update_layout(transition_duration=500)

    return fig


app.layout = html.Div([
    html.H1(
        dcc.RadioItems(
            options=temp_list,
            value=temp_list[0],
            id='ind-settings',
            inline=True,
        ),
    ),
    html.Div(
        dcc.Graph(
            id='candles',
            figure=candle_fig
        ),
    ),
    dcc.Graph(
        id='graph-with-slider',
        figure=fig
    ),
    dash_table.DataTable(
        data = df.to_dict('records'),
        columns = [{"name": i, "id": i} for i in df.columns]
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
