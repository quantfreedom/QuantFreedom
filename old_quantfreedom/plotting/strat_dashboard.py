import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from IPython import get_ipython
from dash import Dash, dcc, html, dash_table
from jupyter_dash import JupyterDash
from plotly.subplots import make_subplots
from dash_bootstrap_templates import load_figure_template

from old_quantfreedom.enums.enums import OrderType
from old_quantfreedom._typing import pdFrame, RecordArray, pdIndex, Array1d

np.set_printoptions(formatter={"float_kind": "{:.2f}".format})

pd.options.display.float_format = "{:,.2f}".format

load_figure_template("darkly")
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
try:
    shell = str(get_ipython())
    if "ZMQInteractiveShell" in shell:
        app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
    elif shell == "TerminalInteractiveShell":
        app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
    else:
        app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
except NameError:
    app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

bg_color = "#0b0b18"


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
    take_profit_array = np.full(array_size, np.nan)

    or_counter = 0
    array_counter = 0

    avg_entry_current = np.array([0.0])
    stop_loss_current = np.array([0.0])
    take_profit_current = np.array([0.0])

    for i in range(array_size):
        if or_counter < order_records.size and order_records["bar"][or_counter] == i:
            fill_candle_trace_trades(
                array_counter=array_counter,
                avg_entry_array=avg_entry_array,
                avg_entry_current=avg_entry_current,
                order_records=order_records[or_counter],
                order_price_array=order_price_array,
                stop_loss_array=stop_loss_array,
                stop_loss_current=stop_loss_current,
                take_profit_array=take_profit_array,
                take_profit_current=take_profit_current,
            )
            or_counter += 1

            if (
                or_counter < order_records.size
                and order_records["bar"][or_counter] == i
            ):
                fill_candle_trace_trades(
                    array_counter=array_counter,
                    avg_entry_array=avg_entry_array,
                    avg_entry_current=avg_entry_current,
                    order_records=order_records[or_counter],
                    order_price_array=order_price_array,
                    stop_loss_array=stop_loss_array,
                    stop_loss_current=stop_loss_current,
                    take_profit_array=take_profit_array,
                    take_profit_current=take_profit_current,
                )
                or_counter += 1
        array_counter += 1
    trace_data_list = cerate_candle_trace_trades_list(
        avg_entry=avg_entry_array,
        index_prices=index_prices,
        order_price_array=order_price_array,
        prices=prices,
        stop_loss=stop_loss_array,
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
    avg_entry_current: Array1d,
    stop_loss_array: Array1d,
    stop_loss_current: Array1d,
    take_profit_array: Array1d,
    take_profit_current: Array1d,
    array_counter: int,
):
    temp_avg_entry = avg_entry_current[0]
    temp_stop_loss = stop_loss_current[0]
    temp_take_profit = take_profit_current[0]

    if temp_avg_entry != order_records["avg_entry"]:
        temp_avg_entry = order_records["avg_entry"]
    else:
        temp_avg_entry = np.nan

    if temp_stop_loss != order_records["sl_price"]:
        temp_stop_loss = order_records["sl_price"]
    else:
        temp_stop_loss = np.nan

    if temp_take_profit != order_records["tp_price"]:
        temp_take_profit = order_records["tp_price"]
    else:
        temp_take_profit = np.nan

    if np.isnan(order_records["real_pnl"]):
        op = order_records["price"]
        ae = temp_avg_entry
        sl = temp_stop_loss
        tp = temp_take_profit

    elif order_records["real_pnl"] > 0 and (
        order_records["order_type"] == OrderType.LongTP
        or order_records["order_type"] == OrderType.ShortTP
    ):
        op = np.nan
        ae = np.nan
        sl = np.nan
        tp = order_records["tp_price"]

    elif not np.isnan(order_records["real_pnl"]):
        op = np.nan
        ae = np.nan
        sl = order_records["sl_price"]
        tp = np.nan

    order_price_array[array_counter] = op
    avg_entry_array[array_counter] = ae
    stop_loss_array[array_counter] = sl
    take_profit_array[array_counter] = tp

    avg_entry_current[0] = order_records["avg_entry"]
    stop_loss_current[0] = order_records["sl_price"]
    take_profit_current[0] = order_records["tp_price"]


def cerate_candle_trace_trades_list(
    index_prices: pdIndex,
    prices: pdFrame,
    order_price_array: Array1d,
    avg_entry: Array1d,
    stop_loss: Array1d,
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
            name="Take Profit",
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


def strat_dashboard(
    indicator_dict: dict,
    prices: pdFrame,
    order_records: RecordArray,
) -> JupyterDash:
    """
    Function Name
    -------------
    strat_dashboard

    Quick Summary
    -------------
    Creates a dashboard with your trades, indicators, cumulative PnL and the order records of all the trades.

    Explainer Video
    ---------------
    Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

    ## Variables needed
    Parameters
    ----------
    indicator_dict : dict
        You need to create a dictionary of all your indicators.

        If you have any indicators that need to go on the candle stick chart then make a key named candle_chart and inside of that you put your indicator values with keys called value with a number after it like in the example, then you provide the entries

        If you have indicators that need their own chart then create a key called indicator with a number after it and then provide the indicator values and the entries in new keys.

        Example:
        ```python
        indicator_dict = {
            "candle_chart": {
                "values1": ema_300_ind[[('BTCUSDT', 300)]],
                "values2": ema_600_ind[[('BTCUSDT', 600)]],
                "entries": entries[[("BTCUSDT", 30, 50, 300, 600)]],
                },
            "indicator1": {
                "values1": rsi_ind[[('BTCUSDT', 30)]],
                "entries": entries[[("BTCUSDT", 30, 50, 300, 600)]],
                },
            "indicator2": {
                "values1": atr_ind[[('BTCUSDT', 50)]],
                "entries": entries[[("BTCUSDT", 30, 50, 300, 600)]],
                },
            }
        ```
    prices : pdFrame
        Your prices info as one symbol like prices['BTCUSDT']
    order_records : RecordArray
        Order Records


    ## Function returns
    Returns
    -------
    JupyterDash
        Returns a jupyter dashboard that will open up in a new window when you click on the local host url
    """

    amount_of_subplots = 0

    for keys in indicator_dict.keys():
        if "indicator" in keys:
            amount_of_subplots += 1

    layout_height = 500 + (250 * amount_of_subplots)
    candle_chart_height_pct = [500 / layout_height]

    if amount_of_subplots > 0:
        subchart_heights_pct = np.array(
            [((layout_height - 500) / layout_height) / amount_of_subplots]
            * amount_of_subplots
        ).tolist()
        row_heights = candle_chart_height_pct + subchart_heights_pct
        fig = make_subplots(
            rows=amount_of_subplots + 1,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=row_heights,
        )
    else:
        fig = make_subplots()

    index_prices = prices.index.to_list()

    # candle chart trace
    fig.add_traces(
        data=get_candle_trace_data(
            index_prices=index_prices,
            prices=prices,
            order_records=order_records,
            indicator_dict=indicator_dict,
        ),
        rows=1,
        cols=1,
    )
    try:
        del indicator_dict["candle_chart"]
    except:
        pass

    row_count = 2
    for indicator_dict_value in indicator_dict.values():
        trace_data_list = []
        temp_ind_vals = np.array([0], dtype=object)
        for ind_key, ind_value in indicator_dict_value.items():
            append_to_trace_data_list(
                trace_data_list=trace_data_list,
                index_prices=index_prices,
                dict_key=ind_key,
                dict_value=ind_value,
                temp_ind_vals=temp_ind_vals,
            )
        fig.add_traces(
            data=trace_data_list,
            rows=row_count,
            cols=1,
        )
        row_count += 1
    fig.update_xaxes(row=1, col=1, rangeslider_visible=False)
    fig.update_yaxes(row=1, col=1, tickprefix="$")
    fig.update_layout(
        height=layout_height,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
    )
    candle_trades_and_ind = (
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
                line=dict(color="#247eb2"),
            ),
        ]
    ).update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
    )
    pnl_graph.update_yaxes(tickprefix="$"),

    pnl_graph = (
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

    d_table = pd.DataFrame(order_records)
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

    app.layout = html.Div(
        [
            html.Div(
                candle_trades_and_ind,
            ),
            html.Div(
                pnl_graph,
            ),
            html.Div(
                d_table,
            ),
        ]
    )

    return app.run_server(debug=True, port=3003)
