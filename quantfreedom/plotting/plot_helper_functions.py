import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from quantfreedom._typing import pdFrame, pdIndex
from quantfreedom.enums.enums import OrderType
from quantfreedom._typing import (
    RecordArray,
    Array1d,
)


def get_candle_trace_data(
    index_prices: pdIndex,
    prices: pdFrame,
    order_records: RecordArray,
    indicator_dict: dict,
) -> list:
    """
    Function Name
    -------------
        get_candle_trace_data

    Quick Summary
    -------------
        Here we take all the info needed to create a candlestick chart and also place indicators on top of the candle stick chart

    Required Parameters
    -------------------
    Variable Name: Variable Type

    index_prices: pdIndex
        index
    prices: pdFrame
        price dataframe
    order_records: RecordArray
        order records
    indicator_dict: dict
        dictionary of candle stick and indicator data

    Returns
    -------
    list
        list of Candle stick chart and indicators data for plotly
    """
    array_size = prices.shape[0]

    order_price_array = np.full(array_size, np.nan)
    avg_entry_array = np.full(array_size, np.nan)
    stop_loss_array = np.full(array_size, np.nan)
    trailing_sl_array = np.full(array_size, np.nan)
    take_profit_array = np.full(array_size, np.nan)

    or_counter = 0
    array_counter = 0

    avg_entry_current = np.array([0.0])
    stop_loss_current = np.array([0.0])
    trailing_sl_current = np.array([0.0])
    take_profit_current = np.array([0.0])

    for i in range(array_size):
        if or_counter < order_records.size and order_records["bar"][or_counter] == i:
            fill_candle_trace_trades(
                order_records=order_records[or_counter],
                order_price_array=order_price_array,
                avg_entry_array=avg_entry_array,
                stop_loss_array=stop_loss_array,
                trailing_sl_array=trailing_sl_array,
                take_profit_array=take_profit_array,
                avg_entry_current=avg_entry_current,
                stop_loss_current=stop_loss_current,
                trailing_sl_current=trailing_sl_current,
                take_profit_current=take_profit_current,
                array_counter=array_counter,
            )
            or_counter += 1

            if (
                or_counter < order_records.size
                and order_records["bar"][or_counter] == i
            ):
                fill_candle_trace_trades(
                    order_records=order_records[or_counter],
                    order_price_array=order_price_array,
                    avg_entry_array=avg_entry_array,
                    stop_loss_array=stop_loss_array,
                    trailing_sl_array=trailing_sl_array,
                    take_profit_array=take_profit_array,
                    avg_entry_current=avg_entry_current,
                    stop_loss_current=stop_loss_current,
                    trailing_sl_current=trailing_sl_current,
                    take_profit_current=take_profit_current,
                    array_counter=array_counter,
                )
            or_counter += 1
        array_counter += 1
    trace_data_list = cerate_candle_trace_trades_list(
        index_prices=index_prices,
        prices=prices,
        order_price_array=order_price_array,
        avg_entry=avg_entry_array,
        stop_loss=stop_loss_array,
        trailing_sl=trailing_sl_array,
        take_profit=take_profit_array,
    )
    if list(indicator_dict.keys())[0] == "candle_chart":
        temp_ind_vals = np.array([0], dtype=object)
        for candle_ind_key, candle_ind_value in indicator_dict["candle_chart"].items():
            append_to_trace_data_list(
                trace_data_list,
                index_prices=index_prices,
                dict_key=candle_ind_key,
                dict_value=candle_ind_value,
                temp_ind_vals=temp_ind_vals,
            )
    return trace_data_list


def fill_candle_trace_trades(
    order_records: RecordArray,
    order_price_array: Array1d,
    avg_entry_array: Array1d,
    stop_loss_array: Array1d,
    trailing_sl_array: Array1d,
    take_profit_array: Array1d,
    avg_entry_current: Array1d,
    stop_loss_current: Array1d,
    trailing_sl_current: Array1d,
    take_profit_current: Array1d,
    array_counter: int,
):
    temp_avg_entry = avg_entry_current[0]
    temp_stop_loss = stop_loss_current[0]
    temp_trailing_sl = trailing_sl_current[0]
    temp_take_profit = take_profit_current[0]

    if temp_avg_entry != order_records["avg_entry"]:
        temp_avg_entry = order_records["avg_entry"]
    else:
        temp_avg_entry = np.nan

    if temp_stop_loss != order_records["sl_prices"]:
        temp_stop_loss = order_records["sl_prices"]
    else:
        temp_stop_loss = np.nan

    if temp_trailing_sl != order_records["tsl_prices"]:
        temp_trailing_sl = order_records["tsl_prices"]
    else:
        temp_trailing_sl = np.nan

    if temp_take_profit != order_records["tp_prices"]:
        temp_take_profit = order_records["tp_prices"]
    else:
        temp_take_profit = np.nan

    if np.isnan(order_records["real_pnl"]):
        op = order_records["price"]
        ae = temp_avg_entry
        sl = temp_stop_loss
        tsl = temp_trailing_sl
        tp = temp_take_profit

    elif order_records["real_pnl"] > 0 and (
        order_records["order_type"] == OrderType.LongTP
        or order_records["order_type"] == OrderType.ShortTP
    ):
        op = np.nan
        ae = np.nan
        sl = np.nan
        tsl = np.nan
        tp = order_records["tp_prices"]

    elif order_records["real_pnl"] > 0 and (
        order_records["order_type"] == OrderType.LongTSL
        or order_records["order_type"] == OrderType.ShortTSL
    ):
        op = np.nan
        ae = np.nan
        sl = np.nan
        tsl = order_records["tsl_prices"]
        tp = np.nan

    elif order_records["real_pnl"] <= 0:
        op = np.nan
        ae = np.nan
        sl = order_records["sl_prices"]
        tsl = order_records["tsl_prices"]
        tp = np.nan

    order_price_array[array_counter] = op
    avg_entry_array[array_counter] = ae
    stop_loss_array[array_counter] = sl
    trailing_sl_array[array_counter] = tsl
    take_profit_array[array_counter] = tp

    avg_entry_current[0] = order_records["avg_entry"]
    stop_loss_current[0] = order_records["sl_prices"]
    trailing_sl_current[0] = order_records["tsl_prices"]
    take_profit_current[0] = order_records["tp_prices"]


def cerate_candle_trace_trades_list(
    index_prices: pdIndex,
    prices: pdFrame,
    order_price_array: Array1d,
    avg_entry: Array1d,
    stop_loss: Array1d,
    trailing_sl: Array1d,
    take_profit: Array1d,
):
    open_prices = prices.open.values
    high_prices = prices.high.values
    low_prices = prices.low.values
    close_prices = prices.close.values

    return [
        go.Candlestick(
            x=index_prices,
            open=open_prices,
            high=high_prices,
            low=low_prices,
            close=close_prices,
            name="Candles",
        ),
        # go.Scatter(
        #     name="Entries",
        #     x=index_prices,
        #     y=order_price_array,
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
        ),
    ]


def append_to_trace_data_list(
    trace_data_list: list,
    dict_key: str,
    dict_value: pdFrame,
    index_prices: pdIndex,
    temp_ind_vals: pdFrame,
):
    """
    Function Name
    -------------
        append_to_trace_data_list

    Quick Summary
    -------------
        appending value or entry scatter plots to the trace data list

    Required Parameters
    -------------------
    Variable Name: Variable Type

    trace_data_list: list
        trace data list
    dict_key: str
        either values or entries
    dict_value: pdFrame
        dataframe of either an indicator or entries
    index_prices: pdIndex
        index
    temp_ind_vals: pdFrame
        needed so we can use this if the dict key is entries so we can generate temp_ind_entries
    """
    if "values" in dict_key:
        temp_ind_vals[0] = dict_value.values.flatten()
        ind_name = list(dict_value.columns.names)[1].split("_")[0]
        ind_value = str(list(dict_value.columns)[0][0])
        trace_data_list.append(
            go.Scatter(
                x=index_prices,
                y=temp_ind_vals[0],
                mode="lines",
                name=ind_name + " " + ind_value,
            )
        )
    elif "entries" in dict_key:
        temp_ind_entries = np.where(
            dict_value.values.flatten(), temp_ind_vals[0], np.nan
        ).flatten()
        trace_data_list.append(
            go.Scatter(
                x=index_prices,
                y=temp_ind_entries,
                mode="markers",
                name="Signals",
            )
        )


def plot_on_candles_1_chart(
    ta_lib_data: pdFrame,
    price_data: pdFrame,
):
    plot_index = price_data.index

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=plot_index,
                open=price_data.iloc[:, -4].values,
                high=price_data.iloc[:, -3].values,
                low=price_data.iloc[:, -2].values,
                close=price_data.iloc[:, -1].values,
                name="Candles",
            ),
            go.Scatter(
                x=plot_index,
                y=ta_lib_data.iloc[:, -1],
                mode="lines",
                line=dict(width=2, color="lightblue"),
            ),
        ]
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_layout(height=500, title="Last Column of the Results")
    fig.show()


def plot_results_candles_and_chart(
    ta_lib_data: pdFrame,
    price_data: pdFrame,
):
    plot_index = price_data.index
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.4],
    )

    fig.add_traces(
        data=go.Candlestick(
            x=plot_index,
            open=price_data.iloc[:, -4].values,
            high=price_data.iloc[:, -3].values,
            low=price_data.iloc[:, -2].values,
            close=price_data.iloc[:, -1].values,
            name="Candles",
        ),
        rows=1,
        cols=1,
    )
    fig.add_traces(
        data=go.Scatter(
            x=plot_index,
            y=ta_lib_data.iloc[:, -1],
            mode="lines",
            line=dict(width=2, color="lightblue"),
        ),
        rows=2,
        cols=1,
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_layout(height=700, title="Last Column of the Results")
    fig.show()
