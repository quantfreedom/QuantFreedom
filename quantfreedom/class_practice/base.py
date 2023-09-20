import pandas as pd
import numpy as np
from typing import Optional
from dash_bootstrap_templates import load_figure_template
from plotly.subplots import make_subplots
from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, dash_table
from IPython import get_ipython
import plotly.io as pio
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from quantfreedom.class_practice.enums import (
    AccountState,
    BacktestSettings,
    CandleBodyType,
    OrderSettingsArrays,
    ExchangeSettings,
    or_dt,
)
from quantfreedom.class_practice.helper_funcs import create_os_cart_product_nb
from quantfreedom.class_practice.simulate import backtest_df_only_nb

pio.renderers.default = "browser"


# np.set_printoptions(formatter={"float_kind": "{:.2f}".format})

# pd.options.display.float_format = "{:,.2f}".format

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


def backtest_df_only(
    account_state: AccountState,
    order_settings_arrays: OrderSettingsArrays,
    backtest_settings: BacktestSettings,
    exchange_settings: ExchangeSettings,
    price_data: pd.DataFrame,
    entries: pd.DataFrame,
    exit_signals: Optional[pd.DataFrame] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    entries = entries.shift(1, fill_value=False)
    print(
        "Creating cartesian product ... after this the backtest will start, I promise :).\n"
    )
    os_cart_arrays = create_os_cart_product_nb(
        order_settings_arrays=order_settings_arrays,
    )

    num_of_symbols = int(price_data.values.shape[1] / 4)

    # Creating Settings Vars
    total_order_settings = os_cart_arrays.risk_account_pct_size.shape[0]

    total_indicator_settings = entries.shape[1]

    total_bars = entries.shape[0]

    if exit_signals is None:
        exit_signals = pd.DataFrame(np.zeros_like(entries.values))

    # Printing out total numbers of things
    print(
        "Starting the backtest now ... and also here are some stats for your backtest.\n"
    )
    print(f"Total symbols: {num_of_symbols:,}")
    print(
        f"Total indicator settings per symbol: {int(total_indicator_settings / num_of_symbols):,}"
    )
    print(f"Total indicator settings to test: {total_indicator_settings:,}")
    print(f"Total order settings per symbol: {total_order_settings:,}")
    print(f"Total order settings to test: {total_order_settings * num_of_symbols:,}")
    print(f"Total candles per symbol: {total_bars:,}")
    print(
        f"Total candles to test: {total_indicator_settings * total_order_settings * total_bars:,}"
    )
    print(
        f"\nTotal combinations to test: {total_indicator_settings * total_order_settings:,}"
    )

    order_records_array, strat_array, settings_array = backtest_df_only_nb(
        account_state=account_state,
        os_cart_arrays=os_cart_arrays,
        backtest_settings=backtest_settings,
        exchange_settings=exchange_settings,
        price_data=price_data.values,
        entries=entries.values,
        exit_signals=exit_signals.values,
        num_of_symbols=num_of_symbols,
        total_bars=total_bars,
        total_indicator_settings=total_indicator_settings,
        total_order_settings=total_order_settings,
    )

    order_records_df = pd.DataFrame(order_records_array, columns=or_dt.names)
    order_records_df = order_records_df[order_records_df.columns[:4]].join(
        order_records_df[order_records_df.columns[4:]].replace(0.0, np.nan)
    )
    strat_results_df = pd.DataFrame(strat_array).sort_values(
        by=["to_the_upside", "gains_pct"],
        ascending=False,
        ignore_index=True,
    )

    symbols = list(price_data.columns.levels[0])

    for i in range(len(symbols)):
        strat_results_df.replace({"symbol": {i: symbols[i]}}, inplace=True)

    setting_results_df = pd.DataFrame(settings_array).dropna(axis="columns", thresh=1)

    for i in range(len(CandleBodyType._fields)):
        setting_results_df.replace(
            {"tsl_based_on": {i: CandleBodyType._fields[i]}}, inplace=True
        )
        setting_results_df.replace(
            {"sl_to_be_based_on": {i: CandleBodyType._fields[i]}}, inplace=True
        )
    for i in range(len(symbols)):
        setting_results_df.replace({"symbol": {i: symbols[i]}}, inplace=True)

    return (
        order_records_df,
        strat_results_df,
        setting_results_df,
    )


def plot_one_result(
    strat_result_index: int,
    strat_res_df: pd.DataFrame,
    price_data: pd.DataFrame,
    order_records_df: pd.DataFrame,
):
    indexes = tuple(strat_res_df.iloc[strat_result_index].iloc[[0, 1, 2]].astype(int))
    index_selected_df = order_records_df[
        (order_records_df.symbol_idx == indexes[0])
        & (order_records_df.ind_set_idx == indexes[1])
        & (order_records_df.or_set_idx == indexes[2])
    ].reset_index()
    price_data_symbol = price_data.columns.levels[0][indexes[0]]
    price_data_index = price_data.index
    results_bar_index = price_data_index[index_selected_df.bar_idx]
    array_with_zeros = np.zeros_like(price_data_index.values, dtype=np.float_)
    pnl_no_nan = index_selected_df[~np.isnan(index_selected_df["realized_pnl"])][
        "realized_pnl"
    ]
    for a, b in pnl_no_nan.items():
        array_with_zeros[index_selected_df["bar_idx"].iloc[a]] = b
    cumsum_pnl_array = array_with_zeros.cumsum()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.6, 0.4],
    )
    fig.add_traces(
        data=[
            go.Candlestick(
                x=price_data_index,
                open=price_data[price_data_symbol].open,
                high=price_data[price_data_symbol].high,
                low=price_data[price_data_symbol].low,
                close=price_data[price_data_symbol].close,
                name="Candles",
            ),
            go.Scatter(
                name="Avg Entries",
                x=results_bar_index,
                y=index_selected_df.average_entry,
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
                x=results_bar_index,
                y=index_selected_df.sl_price,
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
                x=results_bar_index,
                y=index_selected_df.tp_price,
                mode="markers",
                marker=dict(
                    color="#57FF30",
                    size=10,
                    symbol="star",
                    line=dict(color="black", width=1),
                ),
            ),
            go.Scatter(
                name="Exit Hit",
                x=results_bar_index,
                y=index_selected_df.exit_price,
                mode="markers",
                marker=dict(
                    color="yellow",
                    size=10,
                    symbol="square",
                    line=dict(color="black", width=1),
                ),
            ),
        ],
        rows=1,
        cols=1,
    )
    fig.add_traces(
        data=go.Scatter(
            name="PnL",
            x=price_data_index,
            y=cumsum_pnl_array,
            mode="lines+markers",
            marker=dict(size=6),
            line=dict(color="#247eb2"),
        ),
        rows=2,
        cols=1,
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.show()
