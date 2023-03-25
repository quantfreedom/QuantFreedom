import quantfreedom as qf
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output
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

temp_list = []
for count, value in enumerate(list(rsi_ind.columns)):
    temp_list.append(value[0])
print(temp_list)
app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.RadioItems(
        options=temp_list,
        value=temp_list[0],
        id='ind-settings',
        inline=True,
    )
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('ind-settings', 'value'))
def update_figure(selected_ind_settings):
    fig = px.line(
        x=rsi_ind.index.to_list(),
        y=rsi_ind[selected_ind_settings].values.flatten(),
    )

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
