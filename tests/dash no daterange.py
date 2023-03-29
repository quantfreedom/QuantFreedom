import os
import sys

sys.dont_write_bytecode = True
os.environ["NUMBA_DISABLE_JIT"] = "1"
from quantfreedom.backtester.enums.enums import (
    LeverageMode,
    SizeType,
    OrderType,
    SL_BE_or_Trail_BasedOn,
)
from quantfreedom.backtester.evaluators.evaluators import eval_is_below
from quantfreedom.backtester.indicators.talib_ind import from_talib
from quantfreedom.backtester.nb.simulate import simulate_up_to_6
from dash import Dash, dcc, html, Input, Output, dash_table
from plotly.subplots import make_subplots
from datetime import date
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


np.set_printoptions(formatter={"float_kind": "{:.2f}".format})

pd.options.display.float_format = "{:,.2f}".format

load_figure_template('darkly')
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

prices = pd.read_csv(
    "E:/Coding/backtesters/QuantFreedom/tests/data/30min.csv", index_col="time"
)

open_prices = prices.open.values
high_prices = prices.high.values
low_prices = prices.low.values
close_prices = prices.close.values
index_prices = prices.index

rsi_ind = from_talib(
    func_name="rsi",
    df_prices=prices,
    cart_product=False,
    combos=False,
    timeperiod=15,
)
rsi_eval = eval_is_below(
    ind_data=rsi_ind,
    user_args=50,
)

final_array, order_records = simulate_up_to_6(
    open_prices=prices.open.values,
    high_prices=prices.high.values,
    low_prices=prices.low.values,
    close_prices=prices.close.values,
    entries=rsi_eval.values,
    equity=1000.0,
    fee_pct=0.06,
    mmr=0.5,
    lev_mode=LeverageMode.LeastFreeCashUsed,
    size_type=SizeType.RiskPercentOfAccount,
    order_type=OrderType.LongEntry,
    max_equity_risk_pct=4,
    risk_rewards=5,
    size_pct=1.0,
    sl_pcts=3,
)

or_df = pd.DataFrame(order_records)
temp_list = []
for count, value in enumerate(list(rsi_ind.columns)):
    temp_list.append(value[0])



def d_table_update():
    d_table = pd.DataFrame(order_records)
    for i in range(len(OrderType._fields)):
        d_table.replace({"order_type": {i: OrderType._fields[i]}}, inplace=True)

    for col in d_table:
        if d_table[col].dtype == "float64":
            d_table[col] = d_table[col].map("{:,.2f}".format)
    d_table = d_table.to_dict("records")

    d_table = (
        dash_table.DataTable(
            data=d_table,
            id="d-table",
            page_size=50,
            # page_action='none',
            style_table={"height": "400px", "overflowY": "auto"},
            fixed_rows={"headers": True},
            style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
            style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
            style_cell_conditional=[
                {"if": {"column_id": "settings_id"}, "width": "110px"},
                {"if": {"column_id": "order_id"}, "width": "90px"},
            ],
        ),
    )
    return d_table


def pnl_graph():
    y_pnl = np.append(
        0,
        order_records["real_pnl"][~np.isnan(order_records["real_pnl"])].cumsum(),
    )

    pnl_graph = go.Figure(
        data=[
            go.Scatter(
                x=np.arange(0, y_pnl.size),
                y=y_pnl,
                mode="lines+markers",
                marker=dict(size=6),
                line=dict(color="blue"),
            ),
        ],
    ).update_layout(title="PNL Graph")

    return (
        dcc.Graph(
            id="pnl-graph",
            figure=pnl_graph,
        ),
    )


def plot_trades_all_info():

    array_size = open_prices.shape[0]

    order_price = np.full(array_size, np.nan)
    avg_entry = np.full(array_size, np.nan)
    stop_loss = np.full(array_size, np.nan)
    trailing_sl = np.full(array_size, np.nan)
    take_profit = np.full(array_size, np.nan)

    log_counter = 0
    array_counter = 0
    temp_avg_entry = 0
    temp_stop_loss = 0
    temp_trailing_sl = 0
    temp_take_profit = 0

    for i in range(array_size):
        if log_counter < order_records.size and order_records["bar"][log_counter] == i:
            if temp_avg_entry != order_records["avg_entry"][log_counter]:
                temp_avg_entry = order_records["avg_entry"][log_counter]
            else:
                temp_avg_entry = np.nan

            if temp_stop_loss != order_records["sl_prices"][log_counter]:
                temp_stop_loss = order_records["sl_prices"][log_counter]
            else:
                temp_stop_loss = np.nan

            if temp_trailing_sl != order_records["tsl_prices"][log_counter]:
                temp_trailing_sl = order_records["tsl_prices"][log_counter]
            else:
                temp_trailing_sl = np.nan

            if temp_take_profit != order_records["tp_prices"][log_counter]:
                temp_take_profit = order_records["tp_prices"][log_counter]
            else:
                temp_take_profit = np.nan

            if np.isnan(order_records["real_pnl"][log_counter]):
                order_price[array_counter] = order_records["price"][log_counter]
                avg_entry[array_counter] = temp_avg_entry
                stop_loss[array_counter] = temp_stop_loss
                trailing_sl[array_counter] = temp_trailing_sl
                take_profit[array_counter] = temp_take_profit

            elif order_records["real_pnl"][log_counter] > 0 and (
                order_records["order_type"][log_counter] == OrderType.LongTP
                or order_records["order_type"][log_counter] == OrderType.ShortTP
            ):

                order_price[array_counter] = np.nan
                avg_entry[array_counter] = np.nan
                stop_loss[array_counter] = np.nan
                trailing_sl[array_counter] = np.nan
                take_profit[array_counter] = order_records["tp_prices"][log_counter]

            elif order_records["real_pnl"][log_counter] > 0 and (
                order_records["order_type"][log_counter] == OrderType.LongTSL
                or order_records["order_type"][log_counter] == OrderType.ShortTSL
            ):

                order_price[array_counter] = np.nan
                avg_entry[array_counter] = np.nan
                stop_loss[array_counter] = np.nan
                trailing_sl[array_counter] = order_records["tsl_prices"][log_counter]
                take_profit[array_counter] = np.nan

            elif order_records["real_pnl"][log_counter] <= 0:
                order_price[array_counter] = np.nan
                avg_entry[array_counter] = np.nan
                stop_loss[array_counter] = order_records["sl_prices"][log_counter]
                trailing_sl[array_counter] = order_records["tsl_prices"][log_counter]
                take_profit[array_counter] = np.nan

            temp_avg_entry = order_records["avg_entry"][log_counter]
            temp_stop_loss = order_records["sl_prices"][log_counter]
            temp_trailing_sl = order_records["tsl_prices"][log_counter]
            temp_take_profit = order_records["tp_prices"][log_counter]
            log_counter += 1

            if (
                log_counter < order_records.size
                and order_records["bar"][log_counter] == i
            ):
                if temp_avg_entry != order_records["avg_entry"][log_counter]:
                    temp_avg_entry = order_records["avg_entry"][log_counter]
                else:
                    temp_avg_entry = np.nan

                if temp_stop_loss != order_records["sl_prices"][log_counter]:
                    temp_stop_loss = order_records["sl_prices"][log_counter]
                else:
                    temp_stop_loss = np.nan

                if temp_trailing_sl != order_records["tsl_prices"][log_counter]:
                    temp_trailing_sl = order_records["tsl_prices"][log_counter]
                else:
                    temp_trailing_sl = np.nan

                if temp_take_profit != order_records["tp_prices"][log_counter]:
                    temp_take_profit = order_records["tp_prices"][log_counter]
                else:
                    temp_take_profit = np.nan

                if np.isnan(order_records["real_pnl"][log_counter]):
                    order_price[array_counter] = order_records["price"][log_counter]
                    avg_entry[array_counter] = temp_avg_entry
                    stop_loss[array_counter] = temp_stop_loss
                    trailing_sl[array_counter] = temp_trailing_sl
                    take_profit[array_counter] = temp_take_profit

                elif order_records["real_pnl"][log_counter] > 0 and (
                    order_records["order_type"][log_counter] == OrderType.LongTP
                    or order_records["order_type"][log_counter] == OrderType.ShortTP
                ):

                    order_price[array_counter] = np.nan
                    avg_entry[array_counter] = np.nan
                    stop_loss[array_counter] = np.nan
                    trailing_sl[array_counter] = np.nan
                    take_profit[array_counter] = order_records["tp_prices"][log_counter]

                elif order_records["real_pnl"][log_counter] > 0 and (
                    order_records["order_type"][log_counter] == OrderType.LongTSL
                    or order_records["order_type"][log_counter] == OrderType.ShortTSL
                ):

                    order_price[array_counter] = np.nan
                    avg_entry[array_counter] = np.nan
                    stop_loss[array_counter] = np.nan
                    trailing_sl[array_counter] = order_records["tsl_prices"][
                        log_counter
                    ]
                    take_profit[array_counter] = np.nan

                elif order_records["real_pnl"][log_counter] <= 0:
                    order_price[array_counter] = np.nan
                    avg_entry[array_counter] = temp_avg_entry
                    stop_loss[array_counter] = order_records["sl_prices"][log_counter]
                    trailing_sl[array_counter] = order_records["tsl_prices"][
                        log_counter
                    ]
                    take_profit[array_counter] = np.nan

                temp_avg_entry = order_records["avg_entry"][log_counter]
                temp_stop_loss = order_records["sl_prices"][log_counter]
                temp_trailing_sl = order_records["tsl_prices"][log_counter]
                temp_take_profit = order_records["tp_prices"][log_counter]
                log_counter += 1
        array_counter += 1

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3]
    )
    fig.add_traces(
        data=[
            go.Candlestick(
                x=index_prices,
                open=open_prices,
                high=high_prices,
                low=low_prices,
                close=close_prices,
                name="Candles",
                legendgroup="1",
            ),
            go.Scatter(
                name="Entries",
                x=index_prices,
                y=order_price,
                mode="markers",
                marker=dict(
                    color="yellow",
                    size=10,
                    symbol="circle",
                    line=dict(color="black", width=1),
                ),
                legendgroup="1",
            ),
            go.Scatter(
                name="Avg Entries",
                x=index_prices,
                y=avg_entry,
                mode="markers",
                marker=dict(
                    color="#57FF30",
                    size=10,
                    symbol="square",
                    line=dict(color="black", width=1),
                ),
                legendgroup="1",
            ),
            go.Scatter(
                name="Stop Loss",
                x=index_prices,
                y=stop_loss,
                mode="markers",
                marker=dict(
                    color="red",
                    size=10,
                    symbol="x",
                    line=dict(color="black", width=1),
                ),
                legendgroup="1",
            ),
            go.Scatter(
                name="Trailing SL",
                x=index_prices,
                y=trailing_sl,
                mode="markers",
                marker=dict(
                    color="orange",
                    size=10,
                    symbol="triangle-up",
                    line=dict(color="black", width=1),
                ),
                legendgroup="1",
            ),
            go.Scatter(
                name="Take Profits",
                x=index_prices,
                y=take_profit,
                mode="markers",
                marker=dict(
                    color="#57FF30",
                    size=10,
                    symbol="star",
                    line=dict(color="black", width=1),
                ),
                legendgroup="1",
            ),
        ],
        rows=1,
        cols=1,
    )
    fig.add_traces(
        data=[
            go.Scatter(
                x=rsi_ind.index.to_list(),
                y=rsi_ind.values.flatten(),
                mode="lines",
                name="RSI",
                line=dict(color="white"),
                legendgroup="2",
            ),
            go.Scatter(
                x=rsi_ind.index.to_list(),
                y=np.where(rsi_eval.values, rsi_ind.values, np.nan).flatten(),
                mode="markers",
                name="Entries",
                marker=dict(color="darkorange"),
                legendgroup="2",
            ),
        ],
        rows=2,
        cols=1,
    )
    fig.update_xaxes(title_text="Trades", row=1, col=1, rangeslider_visible=False)
    fig.update_layout(height=1000, legend_tracegroupgap=500)

    return (
        dcc.Graph(
            id="candles-trades",
            figure=fig,
        ),
    )


app.layout = html.Div(
    [
        html.Div(
            plot_trades_all_info(),
        ),
        html.Div(
            pnl_graph(),
        ),
        html.Div(
            d_table_update(),
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, port=3003)
