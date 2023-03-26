import os
import sys
sys.dont_write_bytecode = True
os.environ["NUMBA_DISABLE_JIT"] = "1"
from quantfreedom.backtester.evaluators.evaluators import eval_is_below
from quantfreedom.backtester.indicators.talib_ind import from_talib
from quantfreedom.backtester.enums.enums import (
    LeverageMode,
    SizeType,
    OrderType,
    SL_BE_or_Trail_BasedOn,
)
from quantfreedom.backtester.nb.simulate import simulate_up_to_6
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import pandas as pd
import numpy as np


pd.options.display.float_format = '{:,.2f}'.format

prices = pd.read_csv(
    'E:/Coding/backtesters/QuantFreedom/tests/data/30min.csv', index_col='time')

rsi_ind = from_talib(
    func_name='rsi',
    df_prices=prices,
    cart_product=False,
    combos=False,
    timeperiod=15,
)
rsi_eval = eval_is_below(
    rsi_ind,
    np.arange(40, 61, 10),
)
final_array, order_records = simulate_up_to_6(
    open_prices=prices.open.values,
    high_prices=prices.high.values,
    low_prices=prices.low.values,
    close_prices=prices.close.values,
    entries=rsi_eval.values,
    equity=1000.,
    fee_pct=.06,
    mmr=.5,
    lev_mode=LeverageMode.LeastFreeCashUsed,
    size_type=SizeType.RiskPercentOfAccount,
    order_type=OrderType.LongEntry,
    max_equity_risk_pct=4,
    risk_rewards=[3, 5, 6],
    size_pct=1.,
    tsl_true_or_false=True,
    tsl_pcts_init=np.arange(2, 5, 1),
    tsl_based_on=SL_BE_or_Trail_BasedOn.low_price,
    tsl_trail_by_pct=np.arange(1, 4, 1),
    tsl_when_pct_from_avg_entry=np.arange(1, 4, 1),
)

or_df = pd.DataFrame(order_records)
temp_list = []
for count, value in enumerate(list(rsi_ind.columns)):
    temp_list.append(value[0])

# dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
# app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
app = Dash(__name__)

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
    Input('eval-settings', 'value'),
)
def update_ind_figure(selected_eval_settings):
    fig = go.Figure()
    fig.add_scatter(
        x=rsi_ind.index.to_list(),
        y=rsi_ind.values.flatten(),
        mode='lines'
    )
    fig.add_scatter(
        x=rsi_ind.index.to_list(),
        y=np.where(rsi_eval.values[:,selected_eval_settings], rsi_ind.values.flatten(), np.nan),
        mode='markers',
        name='Entries',
        marker=dict(color='green')
    )
    return fig


app.layout = html.Div([
    html.H1(
        dcc.RadioItems(
            options=[0,1,2],
            value=0,
            id='eval-settings',
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
        data=or_df.to_dict('records'),
        page_size=100,
        # page_action='none',
        style_table={'height': '400px', 'overflowY': 'auto'}
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
