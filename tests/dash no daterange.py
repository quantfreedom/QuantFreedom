import os
import sys

sys.dont_write_bytecode = True
os.environ["NUMBA_DISABLE_JIT"] = "1"
from quantfreedom.enums.enums import (
    LeverageMode,
    SizeType,
    OrderType,
)
from quantfreedom.evaluators.evaluators import eval_is_below
from quantfreedom.indicators.talib_ind import from_talib
from quantfreedom.nb.simulate import simulate_up_to_6
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

load_figure_template("darkly")
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])


def strat_dashboard(
    prices,
    eval_results,
    order_records,
    talib_indicator,
):
    global open_prices, high_prices, low_prices, close_prices, index_prices, talib_ind, eval_res, or_rec, bg_color

    bg_color = "#0b0b18"
    open_prices = prices.open.values
    high_prices = prices.high.values
    low_prices = prices.low.values
    close_prices = prices.close.values
    index_prices = prices.index
    talib_ind = talib_indicator
    or_rec = order_records
    eval_res = eval_results


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
        if log_counter < or_rec.size and or_rec["bar"][log_counter] == i:
            if temp_avg_entry != or_rec["avg_entry"][log_counter]:
                temp_avg_entry = or_rec["avg_entry"][log_counter]
            else:
                temp_avg_entry = np.nan

            if temp_stop_loss != or_rec["sl_prices"][log_counter]:
                temp_stop_loss = or_rec["sl_prices"][log_counter]
            else:
                temp_stop_loss = np.nan

            if temp_trailing_sl != or_rec["tsl_prices"][log_counter]:
                temp_trailing_sl = or_rec["tsl_prices"][log_counter]
            else:
                temp_trailing_sl = np.nan

            if temp_take_profit != or_rec["tp_prices"][log_counter]:
                temp_take_profit = or_rec["tp_prices"][log_counter]
            else:
                temp_take_profit = np.nan

            if np.isnan(or_rec["real_pnl"][log_counter]):
                order_price[array_counter] = or_rec["price"][log_counter]
                avg_entry[array_counter] = temp_avg_entry
                stop_loss[array_counter] = temp_stop_loss
                trailing_sl[array_counter] = temp_trailing_sl
                take_profit[array_counter] = temp_take_profit

            elif or_rec["real_pnl"][log_counter] > 0 and (
                or_rec["order_type"][log_counter] == OrderType.LongTP
                or or_rec["order_type"][log_counter] == OrderType.ShortTP
            ):

                order_price[array_counter] = np.nan
                avg_entry[array_counter] = np.nan
                stop_loss[array_counter] = np.nan
                trailing_sl[array_counter] = np.nan
                take_profit[array_counter] = or_rec["tp_prices"][log_counter]

            elif or_rec["real_pnl"][log_counter] > 0 and (
                or_rec["order_type"][log_counter] == OrderType.LongTSL
                or or_rec["order_type"][log_counter] == OrderType.ShortTSL
            ):

                order_price[array_counter] = np.nan
                avg_entry[array_counter] = np.nan
                stop_loss[array_counter] = np.nan
                trailing_sl[array_counter] = or_rec["tsl_prices"][log_counter]
                take_profit[array_counter] = np.nan

            elif or_rec["real_pnl"][log_counter] <= 0:
                order_price[array_counter] = np.nan
                avg_entry[array_counter] = np.nan
                stop_loss[array_counter] = or_rec["sl_prices"][log_counter]
                trailing_sl[array_counter] = or_rec["tsl_prices"][log_counter]
                take_profit[array_counter] = np.nan

            temp_avg_entry = or_rec["avg_entry"][log_counter]
            temp_stop_loss = or_rec["sl_prices"][log_counter]
            temp_trailing_sl = or_rec["tsl_prices"][log_counter]
            temp_take_profit = or_rec["tp_prices"][log_counter]
            log_counter += 1

            if log_counter < or_rec.size and or_rec["bar"][log_counter] == i:
                if temp_avg_entry != or_rec["avg_entry"][log_counter]:
                    temp_avg_entry = or_rec["avg_entry"][log_counter]
                else:
                    temp_avg_entry = np.nan

                if temp_stop_loss != or_rec["sl_prices"][log_counter]:
                    temp_stop_loss = or_rec["sl_prices"][log_counter]
                else:
                    temp_stop_loss = np.nan

                if temp_trailing_sl != or_rec["tsl_prices"][log_counter]:
                    temp_trailing_sl = or_rec["tsl_prices"][log_counter]
                else:
                    temp_trailing_sl = np.nan

                if temp_take_profit != or_rec["tp_prices"][log_counter]:
                    temp_take_profit = or_rec["tp_prices"][log_counter]
                else:
                    temp_take_profit = np.nan

                if np.isnan(or_rec["real_pnl"][log_counter]):
                    order_price[array_counter] = or_rec["price"][log_counter]
                    avg_entry[array_counter] = temp_avg_entry
                    stop_loss[array_counter] = temp_stop_loss
                    trailing_sl[array_counter] = temp_trailing_sl
                    take_profit[array_counter] = temp_take_profit

                elif or_rec["real_pnl"][log_counter] > 0 and (
                    or_rec["order_type"][log_counter] == OrderType.LongTP
                    or or_rec["order_type"][log_counter] == OrderType.ShortTP
                ):

                    order_price[array_counter] = np.nan
                    avg_entry[array_counter] = np.nan
                    stop_loss[array_counter] = np.nan
                    trailing_sl[array_counter] = np.nan
                    take_profit[array_counter] = or_rec["tp_prices"][log_counter]

                elif or_rec["real_pnl"][log_counter] > 0 and (
                    or_rec["order_type"][log_counter] == OrderType.LongTSL
                    or or_rec["order_type"][log_counter] == OrderType.ShortTSL
                ):

                    order_price[array_counter] = np.nan
                    avg_entry[array_counter] = np.nan
                    stop_loss[array_counter] = np.nan
                    trailing_sl[array_counter] = or_rec["tsl_prices"][log_counter]
                    take_profit[array_counter] = np.nan

                elif or_rec["real_pnl"][log_counter] <= 0:
                    order_price[array_counter] = np.nan
                    avg_entry[array_counter] = temp_avg_entry
                    stop_loss[array_counter] = or_rec["sl_prices"][log_counter]
                    trailing_sl[array_counter] = or_rec["tsl_prices"][log_counter]
                    take_profit[array_counter] = np.nan

                temp_avg_entry = or_rec["avg_entry"][log_counter]
                temp_stop_loss = or_rec["sl_prices"][log_counter]
                temp_trailing_sl = or_rec["tsl_prices"][log_counter]
                temp_take_profit = or_rec["tp_prices"][log_counter]
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
            # go.Scatter(
            #     name="Entries",
            #     x=index_prices,
            #     y=order_price,
            #     mode="markers",
            #     marker=dict(
            #         color="yellow",
            #         size=10,
            #         symbol="square",
            #         line=dict(color="black", width=1),
            #     ),
            #     legendgroup="1",
            # ),
            go.Scatter(
                name="Avg Entries",
                x=index_prices,
                y=avg_entry,
                mode="markers",
                marker=dict(
                    color="lightblue",
                    size=10,
                    symbol="circle",
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
                    color="orange",
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
                x=talib_ind.index.to_list(),
                y=talib_ind.values.flatten(),
                mode="lines",
                name="RSI",
                line=dict(color="white"),
                legendgroup="2",
            ),
            go.Scatter(
                x=talib_ind.index.to_list(),
                y=np.where(eval_res.values, talib_ind.values, np.nan).flatten(),
                mode="markers",
                name="Entries",
                marker=dict(color="darkorange"),
                legendgroup="2",
            ),
        ],
        rows=2,
        cols=1,
    )
    fig.update_xaxes(row=1, col=1, rangeslider_visible=False)
    fig.update_layout(
        height=1000,
        legend_tracegroupgap=500,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
    )

    return (
        html.H1(
            "All Trades For This Strategy",
            style={
                "textAlign": "center",
                "font-weight": "bold",
                "font-size": "5em",
                "padding-top": "20px",
            },
        ),
        dcc.Graph(
            id="candles-trades",
            figure=fig,
        ),
    )


def pnl_graph():
    y_pnl = np.append(
        0,
        or_rec["real_pnl"][~np.isnan(or_rec["real_pnl"])].cumsum(),
    )

    pnl_graph = go.Figure(
        data=[
            go.Scatter(
                x=np.arange(0, y_pnl.size),
                y=y_pnl,
                mode="lines+markers",
                marker=dict(size=6),
                line=dict(color="#247eb2"),
            ),
        ]
    ).update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
    )

    return (
        html.H1(
            "Cumulative PnL Over Time",
            style={
                "textAlign": "center",
                "font-weight": "bold",
            },
        ),
        dcc.Graph(
            id="pnl-graph",
            figure=pnl_graph,
        ),
    )


def d_table_update():
    d_table = pd.DataFrame(or_rec)
    for i in range(len(OrderType._fields)):
        d_table.replace({"order_type": {i: OrderType._fields[i]}}, inplace=True)

    for col in d_table:
        if d_table[col].dtype == "float64":
            d_table[col] = d_table[col].map("{:,.2f}".format)
    d_table = d_table.to_dict("records")

    d_table = (
        html.H1(
            "Table of All Orders",
            style={
                "textAlign": "center",
                "font-weight": "bold",
            },
        ),
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
