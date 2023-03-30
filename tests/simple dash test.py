import quantfreedom as qf
import numpy as np
import pandas as pd
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go

from quantfreedom.indicators.talib_ind import from_talib
from quantfreedom._typing import pdFrame, pdSeries

prices = pd.read_csv(
    "E:/Coding/backtesters/QuantFreedom/tests/data/30min.csv", index_col="time"
)
rsi_ind = from_talib(
    func_name="rsi",
    df_prices=prices,
    cart_product=False,
    combos=False,
    timeperiod=[15, 20],
)


fig = go.Figure()

fig.add_candlestick(
    x=prices.index,
    open=prices.open,
    high=prices.high,
    low=prices.low,
    close=prices.close,
    name="Candles",
)
fig.update_layout(
    xaxis=dict(title="Date", rangeslider=dict(visible=False)),
    title="Candles over time",
    autosize=True,
    height=700,
)


def generate_table(dataframe, max_rows=10):
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(col) for col in dataframe.columns])),
            html.Tbody(
                [
                    html.Tr(
                        [html.Td(dataframe.iloc[i][col]) for col in dataframe.columns]
                    )
                    for i in range(min(len(dataframe), max_rows))
                ]
            ),
        ]
    )


app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Quant Freedom"),
        html.Div(
            children="""
        Dash: A web application framework for your data.
    """
        ),
        generate_table(prices),
        dcc.Graph(id="example-graph", figure=fig),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
