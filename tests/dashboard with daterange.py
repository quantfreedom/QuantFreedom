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

np.set_printoptions(formatter={"float_kind": "{:.2f}".format})

pd.options.display.float_format = "{:,.2f}".format

prices = pd.read_csv(
    "E:/Coding/backtesters/QuantFreedom/tests/data/30min.csv", index_col="time"
)

price_index = prices.index.to_list()
index_list = price_index[1:]
start_time = price_index[0].split(" ")[1]
index_time = [start_time]
for x in index_list:
    temp_time = x.split(" ")[1]
    if temp_time == start_time:
        break
    index_time.append(x.split(" ")[1])

price_start_date = price_index[0].split(" ")[0].split("-")
start_year = int(price_start_date[0])
start_month = int(price_start_date[1])
start_day = int(price_start_date[2])

price_end_date = price_index[-1].split(" ")[0].split("-")
end_year = int(price_end_date[0])
end_month = int(price_end_date[1])
end_day = int(price_end_date[2])

rsi_ind = from_talib(
    func_name="rsi",
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
    equity=1000.0,
    fee_pct=0.06,
    mmr=0.5,
    lev_mode=LeverageMode.LeastFreeCashUsed,
    size_type=SizeType.RiskPercentOfAccount,
    order_type=OrderType.LongEntry,
    max_equity_risk_pct=4,
    risk_rewards=[3, 5, 6],
    size_pct=1.0,
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

# app = Dash(__name__)
app = Dash(external_stylesheets=[dbc.themes.CYBORG])


@app.callback(
    Output("candles-figure", "figure"),
    Output("d-table", "data"),
    Output("pnl-graph", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("time-dropdown_start", "value"),
    Input("my-date-picker-range", "end_date"),
    Input("time-dropdown_end", "value"),
)
def update_candles(
    start_date,
    start_time,
    end_date,
    end_time,
):

    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime("%Y-%m-%d ") + start_time
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime("%Y-%m-%d ") + end_time

    start_bar = prices.index.to_list().index(start_date_string)
    end_bar = prices.index.to_list().index(end_date_string)
    filtered_or = order_records[order_records["settings_id"] == 0]
    bar_index = np.where(
        (filtered_or["bar"] >= start_bar) & (filtered_or["bar"] <= end_bar)
    )[0]
    start_bar_index = bar_index[0]
    end_bar_index = bar_index[-1] + 1
    order_records_filtered = filtered_or[start_bar_index:end_bar_index]

    open_prices = prices.open.loc[start_date_string:end_date_string].values
    high_prices = prices.high.loc[start_date_string:end_date_string].values
    low_prices = prices.low.loc[start_date_string:end_date_string].values
    close_prices = prices.close.loc[start_date_string:end_date_string].values
    index_prices = prices.open.loc[start_date_string:end_date_string].index

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[.7,.3]
    )

    (
        candles,
        entries,
        avg_entries,
        stop_losses,
        tailing_stop_losses,
        take_profits,
    ) = plot_trades_all_info(
        open_prices=open_prices,
        high_prices=high_prices,
        low_prices=low_prices,
        close_prices=close_prices,
        index_prices=index_prices,
        order_records=order_records_filtered,
        start_bar=start_bar,
        end_bar=end_bar,
    )
    fig.add_traces(
        data=[
            candles,
            entries,
            avg_entries,
            stop_losses,
            tailing_stop_losses,
            take_profits,
        ],
        rows=1,
        cols=1,
    )
    fig.add_traces(
        data=[
            go.Scatter(
                x=rsi_ind.loc[start_date_string:end_date_string].index.to_list(),
                y=rsi_ind.loc[start_date_string:end_date_string].values.flatten(),
                mode="lines",
                name="RSI",
                line=dict(color="white"),
                legendgroup="2",
            ),
            go.Scatter(
                x=rsi_ind.loc[start_date_string:end_date_string].index.to_list(),
                y=np.where(
                    rsi_eval[15][40].loc[start_date_string:end_date_string].values,
                    rsi_ind.loc[start_date_string:end_date_string].values.flatten(),
                    np.nan,
                ),
                mode="markers",
                name="Entries",
                marker=dict(color="darkorange"),
                legendgroup="2",
            ),
        ],
        rows=2,
        cols=1,
    )
    fig.update_xaxes(
        title_text="xaxis 1 title", row=1, col=1, rangeslider_visible=False
    )
    fig.update_layout(height=1000, legend_tracegroupgap=500, template="plotly_dark")

    d_table = pd.DataFrame(order_records_filtered)
    for i in range(len(OrderType._fields)):
        d_table.replace({"order_type": {i: OrderType._fields[i]}}, inplace=True)

    for col in d_table:
        if d_table[col].dtype == "float64":
            d_table[col] = d_table[col].map("{:,.2f}".format)
    d_table = d_table.to_dict("records")

    upside_y = np.append(
        0,
        order_records_filtered["real_pnl"][
            ~np.isnan(order_records_filtered["real_pnl"])
        ].cumsum(),
    )

    pnl_graph = go.Figure(
        data=[
            go.Scatter(
                x=np.arange(0, upside_y.size),
                y=upside_y,
                mode="lines+markers",
                marker=dict(size=6),
                line=dict(color="blue"),
            ),
        ],
    ).update_layout(title="PNL Graph", template="plotly_dark")
    return fig, d_table, pnl_graph


def plot_trades_all_info(
    open_prices,
    high_prices,
    low_prices,
    close_prices,
    index_prices,
    order_records,
    start_bar,
    end_bar,
):

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

    for i in range(start_bar, end_bar):
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

    candles = go.Candlestick(
        x=index_prices,
        open=open_prices,
        high=high_prices,
        low=low_prices,
        close=close_prices,
        name="Candles",
        legendgroup="1",
    )

    # entries
    entries = go.Scatter(
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
    )

    # avg entrys
    avg_entries = go.Scatter(
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
    )

    # stop loss
    stop_losses = go.Scatter(
        name="Stop Loss",
        x=index_prices,
        y=stop_loss,
        mode="markers",
        marker=dict(
            color="red", size=10, symbol="x", line=dict(color="black", width=1)
        ),
        legendgroup="1",
    )

    # trailing stop loss
    tailing_stop_losses = go.Scatter(
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
    )

    # take profits
    take_profits = go.Scatter(
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
    )

    return candles, entries, avg_entries, stop_losses, tailing_stop_losses, take_profits


app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H2("Date Range"),
                    ],
                    style=(
                        {
                            "display": "flex",
                            "justify-content": "center",
                        }
                    ),
                ),
                html.Div(
                    [
                        dcc.DatePickerRange(
                            id="my-date-picker-range",
                            month_format="MM-DD-YYYY",
                            display_format="MM-DD-YYYY",
                            start_date=date(start_year, start_month, start_day),
                            end_date=date(end_year, end_month, end_day),
                            min_date_allowed=date(start_year, start_month, start_day),
                            max_date_allowed=date(end_year, end_month, end_day),
                            with_portal=True,
                        ),
                    ],
                    style=(
                        {
                            "display": "flex",
                            "justify-content": "center",
                        }
                    ),
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=index_time,
                                    value=index_time[0],
                                    id="time-dropdown_start",
                                ),
                            ],
                            style=(
                                {
                                    "width": "145px",
                                }
                            ),
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=index_time,
                                    value=index_time[-1],
                                    id="time-dropdown_end",
                                ),
                            ],
                            style=(
                                {
                                    "width": "145px",
                                }
                            ),
                        ),
                    ],
                    style=(
                        {
                            "display": "flex",
                            "margin": "auto",
                            "width": "auto",
                            "justify-content": "center",
                        }
                    ),
                ),
            ],
        ),
        html.Div(
            dcc.Graph(
                id="candles-figure",
            ),
        ),
        html.Div(
            dcc.Graph(
                id="pnl-graph",
            ),
        ),
        dash_table.DataTable(
            id="d-table",
            page_size=100,
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
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, port=1064)
