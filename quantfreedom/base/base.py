import numpy as np
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from quantfreedom.nb.simulate import backtest_df_only_nb
from quantfreedom.nb.helper_funcs import (
    static_var_checker_nb,
    create_1d_arrays_nb,
    check_1d_arrays_nb,
    create_cart_product_nb,
)
from quantfreedom._typing import (
    plSeries,
    pdFrame,
    RecordArray,
    PossibleArray,
)
from quantfreedom.enums.enums import OrderType, SL_BE_or_Trail_BasedOn


def backtest_df_only(
    # entry info
    entries: pdFrame,
    prices: pdFrame,
    # required account info
    equity: float,
    fee_pct: float,
    mmr: float,
    # required order
    lev_mode: int,
    order_type: int,
    size_type: int,
    # Order Params
    leverage: PossibleArray = np.nan,
    max_equity_risk_pct: PossibleArray = np.nan,
    max_equity_risk_value: PossibleArray = np.nan,
    max_order_size_pct: float = 100.0,
    min_order_size_pct: float = 0.01,
    max_order_size_value: float = np.inf,
    min_order_size_value: float = 1.0,
    max_lev: float = 100.0,
    size_pct: PossibleArray = np.nan,
    size_value: PossibleArray = np.nan,
    # Stop Losses
    sl_pcts: PossibleArray = np.nan,
    sl_to_be: bool = False,
    sl_to_be_based_on: PossibleArray = np.nan,
    sl_to_be_when_pct_from_avg_entry: PossibleArray = np.nan,
    sl_to_be_zero_or_entry: PossibleArray = np.nan,
    sl_to_be_then_trail: bool = False,
    sl_to_be_trail_by_when_pct_from_avg_entry: PossibleArray = np.nan,
    # Trailing Stop Loss Params
    tsl_pcts_init: PossibleArray = np.nan,
    tsl_true_or_false: bool = False,
    tsl_based_on: PossibleArray = np.nan,
    tsl_trail_by_pct: PossibleArray = np.nan,
    tsl_when_pct_from_avg_entry: PossibleArray = np.nan,
    # Take Profit Params
    risk_rewards: PossibleArray = np.nan,
    tp_pcts: PossibleArray = np.nan,
    # Results Filters
    gains_pct_filter: float = -np.inf,
    total_trade_filter: int = 0,
):
    print("Checking static variables for errors or conflicts.")
    # Static checks
    static_variables_tuple = static_var_checker_nb(
        equity=equity,
        fee_pct=fee_pct,
        mmr=mmr,
        lev_mode=lev_mode,
        order_type=order_type,
        size_type=size_type,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        min_order_size_pct=min_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_value=min_order_size_value,
        sl_to_be=sl_to_be,
        sl_to_be_then_trail=sl_to_be_then_trail,
        tsl_true_or_false=tsl_true_or_false,
        gains_pct_filter=gains_pct_filter,
        total_trade_filter=total_trade_filter,
    )
    print("Turning all variables into arrays.")
    # Create 1d Arrays
    arrays_1d_tuple = create_1d_arrays_nb(
        leverage=leverage,
        max_equity_risk_pct=max_equity_risk_pct,
        max_equity_risk_value=max_equity_risk_value,
        risk_rewards=risk_rewards,
        size_pct=size_pct,
        size_value=size_value,
        sl_pcts=sl_pcts,
        sl_to_be_based_on=sl_to_be_based_on,
        sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry,
        sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry,
        sl_to_be_zero_or_entry=sl_to_be_zero_or_entry,
        tp_pcts=tp_pcts,
        tsl_based_on=tsl_based_on,
        tsl_pcts_init=tsl_pcts_init,
        tsl_trail_by_pct=tsl_trail_by_pct,
        tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry,
    )
    print(
        "Checking arrays for errors or conflicts ... the backtest will begin shortly, please hold."
    )
    # Checking all new arrays
    check_1d_arrays_nb(
        static_variables_tuple=static_variables_tuple,
        arrays_1d_tuple=arrays_1d_tuple,
    )

    print(
        "Creating cartesian product ... after this the backtest will start, I promise :).\n"
    )
    cart_array_tuple = create_cart_product_nb(arrays_1d_tuple=arrays_1d_tuple)

    num_of_symbols = len(prices.columns.levels[0])

    # Creating Settings Vars
    total_order_settings = cart_array_tuple.sl_pcts.shape[0]

    total_indicator_settings = entries.shape[1]

    total_bars = entries.shape[0]

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

    strat_array, settings_array = backtest_df_only_nb(
        num_of_symbols=num_of_symbols,
        total_indicator_settings=total_indicator_settings,
        total_order_settings=total_order_settings,
        total_bars=total_bars,
        og_equity=equity,
        entries=entries.values,
        prices=prices.values,
        gains_pct_filter=gains_pct_filter,
        total_trade_filter=total_trade_filter,
        static_variables_tuple=static_variables_tuple,
        cart_array_tuple=cart_array_tuple,
    )

    strat_results_df = pd.DataFrame(strat_array).sort_values(
        by=["to_the_upside", "gains_pct"], ascending=False
    )

    symbols = list(prices.columns.levels[0])

    for i in range(len(symbols)):
        strat_results_df.replace({"symbol": {i: symbols[i]}}, inplace=True)

    symbols = list(entries.columns.levels[0])
    setting_results_df = pd.DataFrame(settings_array).dropna(axis="columns", thresh=1)

    for i in range(len(SL_BE_or_Trail_BasedOn._fields)):
        setting_results_df.replace(
            {"tsl_based_on": {i: SL_BE_or_Trail_BasedOn._fields[i]}}, inplace=True
        )
        setting_results_df.replace(
            {"sl_to_be_based_on": {i: SL_BE_or_Trail_BasedOn._fields[i]}}, inplace=True
        )
    for i in range(len(symbols)):
        setting_results_df.replace({"symbol": {i: symbols[i]}}, inplace=True)

    setting_results_df = setting_results_df.T

    return strat_results_df, setting_results_df


def plot_trades_all_info(
    open_prices: plSeries,
    high_prices: plSeries,
    low_prices: plSeries,
    close_prices: plSeries,
    order_records: RecordArray,
):
    start = order_records["bar"].min() - 2
    end = order_records["bar"].max() + 3

    x_index = open_prices.index[start:end]
    open_prices = open_prices[start:end]
    high_prices = high_prices[start:end]
    low_prices = low_prices[start:end]
    close_prices = close_prices[start:end]

    array_size = end - start

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

    for i in range(start, end):
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
    fig.show()


def replay_trade_plotter(
    open_prices,
    high_prices,
    low_prices,
    close_prices,
    order_records,
):
    start = order_records["bar"].min() - 2
    end = order_records["bar"].max() + 3

    x_index = open_prices.index[start:end]
    open_prices = open_prices[start:end]
    high_prices = high_prices[start:end]
    low_prices = low_prices[start:end]
    close_prices = close_prices[start:end]

    order_price = np.full(end - start, np.nan)
    avg_entry = np.full(end - start, np.nan)
    stop_loss = np.full(end - start, np.nan)
    trailing_sl = np.full(end - start, np.nan)
    take_profit = np.full(end - start, np.nan)

    log_counter = 0
    array_counter = 0
    temp_avg_entry = 0
    temp_stop_loss = 0
    temp_trailing_sl = 0
    temp_take_profit = 0

    for i in range(start, end):
        if (
            log_counter <= order_records["order_id"].max()
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
                temp_take_profit = np.nan

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
                avg_entry[array_counter] = temp_avg_entry
                stop_loss[array_counter] = temp_stop_loss
                trailing_sl[array_counter] = temp_trailing_sl
                take_profit[array_counter] = order_records["tp_prices"][log_counter]

            elif order_records["real_pnl"][log_counter] > 0 and (
                order_records["order_type"][log_counter] == OrderType.LongTSL
                or order_records["order_type"][log_counter] == OrderType.ShortTSL
            ):
                order_price[array_counter] = np.nan
                avg_entry[array_counter] = temp_avg_entry
                stop_loss[array_counter] = temp_stop_loss
                trailing_sl[array_counter] = order_records["tsl_prices"][log_counter]
                take_profit[array_counter] = temp_take_profit

            elif order_records["real_pnl"][log_counter] <= 0:
                order_price[array_counter] = np.nan
                avg_entry[array_counter] = temp_avg_entry
                stop_loss[array_counter] = order_records["sl_prices"][log_counter]
                trailing_sl[array_counter] = order_records["tsl_prices"][log_counter]
                take_profit[array_counter] = temp_take_profit

            temp_avg_entry = order_records["avg_entry"][log_counter]
            temp_stop_loss = order_records["sl_prices"][log_counter]
            temp_trailing_sl = order_records["tsl_prices"][log_counter]
            temp_take_profit = order_records["tp_prices"][log_counter]
            log_counter += 1
            if (
                log_counter <= order_records["order_id"].max()
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
                    temp_take_profit = np.nan

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
                    avg_entry[array_counter] = temp_avg_entry
                    stop_loss[array_counter] = temp_stop_loss
                    trailing_sl[array_counter] = temp_trailing_sl
                    take_profit[array_counter] = order_records["tp_prices"][log_counter]

                elif order_records["real_pnl"][log_counter] > 0 and (
                    order_records["order_type"][log_counter] == OrderType.LongTSL
                    or order_records["order_type"][log_counter] == OrderType.ShortTSL
                ):
                    order_price[array_counter] = np.nan
                    avg_entry[array_counter] = temp_avg_entry
                    stop_loss[array_counter] = temp_stop_loss
                    trailing_sl[array_counter] = order_records["tsl_prices"][
                        log_counter
                    ]
                    take_profit[array_counter] = temp_take_profit

                elif order_records["real_pnl"][log_counter] <= 0:
                    order_price[array_counter] = np.nan
                    avg_entry[array_counter] = temp_avg_entry
                    stop_loss[array_counter] = order_records["sl_prices"][log_counter]
                    trailing_sl[array_counter] = order_records["tsl_prices"][
                        log_counter
                    ]
                    take_profit[array_counter] = temp_take_profit

                temp_avg_entry = order_records["avg_entry"][log_counter]
                temp_stop_loss = order_records["sl_prices"][log_counter]
                temp_trailing_sl = order_records["tsl_prices"][log_counter]
                temp_take_profit = order_records["tp_prices"][log_counter]
                log_counter += 1
        array_counter += 1

    play_button = {
        "args": [
            None,
            {
                "frame": {"duration": 150, "redraw": True},
                "fromcurrent": True,
                "transition": {"duration": 0, "easing": "quadratic-in-out"},
            },
        ],
        "label": "Play",
        "method": "animate",
    }

    pause_button = {
        "args": [
            [None],
            {
                "frame": {"duration": 0, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 0},
            },
        ],
        "label": "Pause",
        "method": "animate",
    }

    sliders_steps = [
        {
            "args": [
                [0, i],  # 0, in order to reset the image, i in order to plot frame i
                {
                    "frame": {"duration": 150, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 0},
                },
            ],
            "label": i,
            "method": "animate",
        }
        for i in range(order_price.size)
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "candle:",
            "visible": True,
            "xanchor": "right",
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": sliders_steps,
    }

    fig = go.Figure()

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
            color="yellow", size=10, symbol="circle", line=dict(color="black", width=2)
        ),
    )

    # avg entrys
    fig.add_scatter(
        name="Avg Entries",
        x=x_index,
        y=avg_entry,
        mode="markers",
        marker=dict(
            color="#57FF30", size=10, symbol="square", line=dict(color="black", width=2)
        ),
    )

    # stop loss
    fig.add_scatter(
        name="Stop Loss",
        x=x_index,
        y=stop_loss,
        mode="markers",
        marker=dict(
            color="red", size=10, symbol="x", line=dict(color="black", width=2)
        ),
    )

    # trailing stop loss
    fig.add_scatter(
        name="Trailing SL",
        x=x_index,
        y=trailing_sl,
        mode="markers",
        marker=dict(
            color="orange", size=10, symbol="x", line=dict(color="black", width=2)
        ),
    )

    # take profits
    fig.add_scatter(
        name="Take Profits",
        x=x_index,
        y=take_profit,
        mode="markers",
        marker=dict(
            color="#57FF30", size=10, symbol="star", line=dict(color="black", width=2)
        ),
    )

    fig.update_layout(
        xaxis=dict(title="Date", rangeslider=dict(visible=False)),
        title="Candles over time",
        updatemenus=[dict(type="buttons", buttons=[play_button, pause_button])],
        sliders=[sliders_dict],
        height=600,
    )

    for_loop_len = order_price.size
    for x in range(15, 0, -1):
        if for_loop_len % x == 0:
            for_loop_steps = x
            break

    frames = []
    print(for_loop_len)
    print(for_loop_steps)
    for i in range(0, for_loop_len + 1, for_loop_steps):
        frames.append(
            # name, I imagine, is used to bind to frame i :)
            go.Frame(
                data=[
                    go.Candlestick(
                        x=x_index,
                        open=open_prices[:i],
                        high=high_prices[:i],
                        low=low_prices[:i],
                        close=close_prices[:i],
                    ),
                    go.Scatter(
                        x=x_index,
                        y=order_price[:i],
                    ),
                    go.Scatter(
                        x=x_index,
                        y=avg_entry[:i],
                    ),
                    go.Scatter(
                        x=x_index,
                        y=stop_loss[:i],
                    ),
                    go.Scatter(
                        x=x_index,
                        y=trailing_sl[:i],
                    ),
                    go.Scatter(
                        x=x_index,
                        y=take_profit[:i],
                    ),
                ],
                traces=[0, 1, 2, 3, 4],
                name=f"{i}",
            )
        )
    fig.update(frames=frames)
    fig.show()
