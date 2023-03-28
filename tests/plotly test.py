import os
import sys

sys.dont_write_bytecode = True
os.environ["NUMBA_DISABLE_JIT"] = "1"
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from plotly.subplots import make_subplots

from dash import Dash, dcc, html, Input, Output, dash_table
from quantfreedom.backtester.nb.simulate import simulate_up_to_6
from quantfreedom.backtester.indicators.talib_ind import from_talib
from quantfreedom.backtester.evaluators.evaluators import eval_is_below
from quantfreedom._typing import pdFrame, RecordArray
from quantfreedom.backtester.enums.enums import (
    LeverageMode,
    SizeType,
    OrderType,
    SL_BE_or_Trail_BasedOn,
)

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

app = Dash(__name__)


@app.callback(
    Output("candles-figure", "figure"),
    Output("d-table", "data"),
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
    or_df=or_df,
):

    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime("%Y-%m-%d ") + start_time
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime("%Y-%m-%d ") + end_time

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        # specs=[[{"type": "scatter"}], [{"type": "scatter"}], [{"type": "table"}]],
    )
    fig.add_trace(
        go.Candlestick(
            x=prices.loc[start_date_string:end_date_string].index,
            open=prices.open.loc[start_date_string:end_date_string],
            high=prices.high.loc[start_date_string:end_date_string],
            low=prices.low.loc[start_date_string:end_date_string],
            close=prices.close.loc[start_date_string:end_date_string],
            name="Candles",
        ),
        
        row=1,
        col=1,
    )
    
    fig.add_traces(
        data=[
            go.Scatter(
                x=rsi_ind.loc[start_date_string:end_date_string].index.to_list(),
                y=rsi_ind.loc[start_date_string:end_date_string].values.flatten(),
                mode="lines",
            ),
            go.Scatter(
                x=rsi_ind.loc[start_date_string:end_date_string].index.to_list(),
                y=np.where(
                    rsi_eval[15][50].loc[start_date_string:end_date_string].values,
                    rsi_ind.loc[start_date_string:end_date_string].values.flatten(),
                    np.nan,
                ),
                mode="markers",
                name="Entries",
                marker=dict(color="green"),
            ),
        ],
        rows=2,
        cols=1,
    )
    # headerColor = "grey"
    # rowEvenColor = "lightgrey"
    # rowOddColor = "white"
    # fig.add_traces(
    #     data=[
    #         go.Table(
    #             header=dict(
    #                 values=(order_records.dtype.names),
    #                 line_color="darkslategray",
    #                 fill_color=headerColor,
    #                 align=["left", "center"],
    #                 font=dict(color="white", size=20),
    #             ),
    #             cells=dict(
    #                 values=pd.DataFrame(order_records[:20]).T.values,
    #                 line_color="darkslategray",
    #                 # 2-D list of colors for alternating rows
    #                 # fill_color=[
    #                 #     [
    #                 #         rowOddColor,
    #                 #         rowEvenColor,
    #                 #         rowOddColor,
    #                 #         rowEvenColor,
    #                 #         rowOddColor,
    #                 #     ]
    #                 #     * 5
    #                 # ],
    #                 align=["left", "center"],
    #                 font=dict(color="darkslategray", size=15),
    #             ),
    #         )
    #     ],
    #     rows=3,
    #     cols=1,
    # ),
    fig.update_xaxes(
        title_text="xaxis 1 title", row=1, col=1, rangeslider_visible=False
    )
    fig.update_layout(height=1000)
    d_table = or_df.to_dict("records")
    return fig, d_table


@app.callback(
    Output("plotted-trades", "figure"),
    Input("thing-thing", "value"),
    Input("thing-thing", "value"),
    Input("thing-thing", "value"),
)
def plot_trades_all_info(
    start_date,
    # end_date,
    # prices: pdFrame,
    # order_records: RecordArray,
):
    global prices, order_records
    start = prices.index[30]
    end = prices.index[200]

    start_bar = prices.index.to_list().index(start)
    end_bar = prices.index.to_list().index(end)
    bar_index = np.where(
        (order_records["bar"] >= start_bar) & (order_records["bar"] <= end_bar)
    )[0]
    start_bar_index = bar_index[0]
    end_bar_index = bar_index[-1] + 1
    order_records = order_records[start_bar_index:end_bar_index]

    open_prices = prices.open.loc[start:end].values
    high_prices = prices.high.loc[start:end].values
    low_prices = prices.low.loc[start:end].values
    close_prices = prices.close.loc[start:end].values
    x_index = prices.open.loc[start:end].index

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

    fig = go.Figure()

    symbol_size = 10

    fig.add_candlestick(
        x=x_index,
        open=open_prices,
        high=high_prices,
        low=low_prices,
        close=close_prices,
        name="Candles",
    )

    # entries
    fig.add_scatter(
        name="Entries",
        x=x_index,
        y=order_price,
        mode="markers",
        marker=dict(
            color="yellow",
            size=symbol_size,
            symbol="circle",
            line=dict(color="black", width=2),
        ),
    )

    # avg entrys
    fig.add_scatter(
        name="Avg Entries",
        x=x_index,
        y=avg_entry,
        mode="markers",
        marker=dict(
            color="#57FF30",
            size=symbol_size,
            symbol="square",
            line=dict(color="black", width=2),
        ),
    )

    # stop loss
    fig.add_scatter(
        name="Stop Loss",
        x=x_index,
        y=stop_loss,
        mode="markers",
        marker=dict(
            color="red", size=symbol_size, symbol="x", line=dict(color="black", width=2)
        ),
    )

    # trailing stop loss
    fig.add_scatter(
        name="Trailing SL",
        x=x_index,
        y=trailing_sl,
        mode="markers",
        marker=dict(
            color="orange",
            size=symbol_size,
            symbol="triangle-up",
            line=dict(color="black", width=2),
        ),
    )

    # take profits
    fig.add_scatter(
        name="Take Profits",
        x=x_index,
        y=take_profit,
        mode="markers",
        marker=dict(
            color="#57FF30",
            size=symbol_size,
            symbol="star",
            line=dict(color="black", width=2),
        ),
    )

    fig.update_layout(
        xaxis=dict(title="Date", rangeslider=dict(visible=False)),
        title="Candles over time",
        autosize=True,
        height=600,
    )
    return fig


app.layout = html.Div(
    [
        html.Div(
            [
                dcc.DatePickerRange(
                    month_format="MM-DD-YYYY",
                    display_format="MM-DD-YYYY",
                    start_date=date(start_year, start_month, start_day),
                    end_date=date(end_year, end_month, end_day),
                    min_date_allowed=date(start_year, start_month, start_day),
                    max_date_allowed=date(end_year, end_month, end_day),
                    id="my-date-picker-range",
                    # initial_visible_month=date(start_year, start_month, start_day),
                ),
            ]
        ),
        html.Div(
            [
                dcc.Dropdown(
                    options=index_time,
                    value=index_time[0],
                    id="time-dropdown_start",
                ),
                dcc.Dropdown(
                    options=index_time,
                    value=index_time[-1],
                    id="time-dropdown_end",
                ),
            ],
            style={"width": "20%", "display": "inline-block"},
        ),
        html.Div(
            dcc.Graph(
                id="candles-figure",
            ),
        ),
        dash_table.DataTable(
            id="d-table",
            page_size=100,
            # page_action='none',
            style_table={"height": "400px", "overflowY": "auto"},
            fixed_rows={'headers': True},
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, port=3003)
