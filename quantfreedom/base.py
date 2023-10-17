import pandas as pd
import numpy as np
from dash_bootstrap_templates import load_figure_template
from plotly.subplots import make_subplots
from jupyter_dash import JupyterDash
from dash import Dash
from IPython import get_ipython
import plotly.io as pio
import dash_bootstrap_components as dbc
import logging
from quantfreedom.enums import *
from quantfreedom.helper_funcs import get_order_setting, get_to_the_upside_nb
from quantfreedom.order_handler.order_handler import Order
from quantfreedom.strategies.strategy import Strategy

info_logger = logging.getLogger("info")

from quantfreedom.enums import (
    BacktestSettings,
    OrderSettingsArrays,
    ExchangeSettings,
)
from quantfreedom.strategies.strategy import Strategy

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


def starting_bar_backtest(num_candles: int):
    return 0


def starting_bar_real(num_candles: int):
    return num_candles - 1


def backtest_df_only(
    starting_equity: float,
    os_cart_arrays: OrderSettingsArrays,
    backtest_settings: BacktestSettings,
    exchange_settings: ExchangeSettings,
    strategy: Strategy,
    candles: np.array,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Creating Settings Vars
    total_order_settings = os_cart_arrays[0].size

    total_indicator_settings = strategy.indicator_cart_product[0].size

    total_bars = candles.size

    # Printing out total numbers of things
    print("Starting the backtest now ... and also here are some stats for your backtest.\n")
    print(f"Total indicator settings to test: {total_indicator_settings:,}")
    print(f"Total order settings to test: {total_order_settings:,}")
    print(f"Total combinations of settings to test: {total_indicator_settings * total_order_settings:,}")
    print(f"\nTotal candles: {total_bars:,}")
    print(f"Total candles to test: {total_indicator_settings * total_order_settings * total_bars:,}")

    array_size = int(total_indicator_settings * total_order_settings / backtest_settings.divide_records_array_size_by)

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )

    result_records_filled = 0

    strat_records = np.empty(int(total_bars / 2), dtype=strat_records_dt)

    if strategy.candle_processing_mode == CandleProcessingType.Backtest:
        calc_starting_bar = starting_bar_backtest
    else:
        calc_starting_bar = starting_bar_real

    for indicator_settings_index in range(total_indicator_settings):
        info_logger.debug(f"Indicator settings index = {indicator_settings_index:,}")
        strategy.set_indicator_settings(indicator_settings_index=indicator_settings_index)

        for order_settings_index in range(total_order_settings):
            info_logger.debug(f"Order settings index = {order_settings_index:,}")
            order_settings = get_order_setting(
                order_settings_index=order_settings_index,
                os_cart_arrays=os_cart_arrays,
            )

            order = Order.instantiate(
                equity=starting_equity,
                order_settings=order_settings,
                exchange_settings=exchange_settings,
                long_or_short=order_settings.long_or_short,
                strat_records=strat_records,
            )

            info_logger.debug(f"Created Order class")

            starting_bar = calc_starting_bar(order_settings.num_candles)

            # entries loop
            for bar_index in range(starting_bar, total_bars):
                info_logger.debug(
                    f"ind_idx={indicator_settings_index:,} os_idx={order_settings_index:,} b_idx={bar_index} timestamp={pd.to_datetime(candles['timestamp'][bar_index], unit='ms')}"
                )
                if order.position_size_usd > 0:
                    try:
                        order.check_stop_loss_hit(current_candle=candles[bar_index])
                        order.check_liq_hit(current_candle=candles[bar_index])
                        order.check_take_profit_hit(
                            current_candle=candles[bar_index],
                            exit_signal=strategy.current_exit_signals[bar_index],
                        )
                        order.check_move_stop_loss_to_be(bar_index=bar_index, candles=candles)
                        order.check_move_trailing_stop_loss(bar_index=bar_index, candles=candles)
                    except RejectedOrder as e:
                        info_logger.warning(f"RejectedOrder -> {e.msg}")
                        pass
                    except DecreasePosition as e:
                        order.decrease_position(
                            order_status=e.order_status,
                            exit_price=e.exit_price,
                            exit_fee_pct=e.exit_fee_pct,
                            bar_index=bar_index,
                            timestamp=candles["timestamp"][bar_index],
                            indicator_settings_index=indicator_settings_index,
                            order_settings_index=order_settings_index,
                        )
                    except MoveStopLoss as e:
                        order.move_stop_loss(
                            sl_price=e.sl_price,
                            order_status=e.order_status,
                            bar_index=bar_index,
                            timestamp=candles["timestamp"][bar_index],
                            order_settings_index=order_settings_index,
                            indicator_settings_index=indicator_settings_index,
                        )
                    except Exception as e:
                        info_logger.error(f"Exception placing order -> {e}")
                        raise Exception(f"Exception placing order -> {e}")
                strategy.create_indicator(bar_index=bar_index, starting_bar=starting_bar)
                if strategy.evaluate():  # add in that we are also not at max entry amount
                    try:
                        order.calculate_stop_loss(bar_index=bar_index, candles=candles)
                        order.calculate_increase_posotion(entry_price=candles["close"][bar_index])
                        order.calculate_leverage()
                        order.calculate_take_profit()

                    except RejectedOrder as e:
                        info_logger.warning(f"RejectedOrder -> {e.msg}")
                        pass
                    except Exception as e:
                        info_logger.error(f"Exception placing order -> {e}")
                        raise Exception(f"Exception placing order -> {e}")
            # Checking if gains
            gains_pct = round(((order.equity - starting_equity) / starting_equity) * 100, 2)
            info_logger.debug(f"Starting eq={starting_equity} Ending eq={order.equity} gains pct={gains_pct}")
            if gains_pct > backtest_settings.gains_pct_filter:
                temp_strat_records = order.strat_records[: order.strat_records_filled]
                pnl_array = temp_strat_records["real_pnl"]
                wins_and_losses_array = pnl_array[~np.isnan(temp_strat_records["real_pnl"])]

                # Checking total trade filter
                if wins_and_losses_array.size > backtest_settings.total_trade_filter:
                    wins_and_losses_array_no_be = wins_and_losses_array[wins_and_losses_array != 0]
                    to_the_upside = get_to_the_upside_nb(
                        gains_pct=gains_pct,
                        wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                    )

                    # Checking to the upside filter
                    if to_the_upside > backtest_settings.upside_filter:
                        win_loss = np.where(wins_and_losses_array_no_be < 0, 0, 1)
                        win_rate = round(np.count_nonzero(win_loss) / win_loss.size * 100, 2)
                        total_pnl = pnl_array.sum()

                        # strat array
                        strategy_result_records[result_records_filled]["ind_set_idx"] = indicator_settings_index
                        strategy_result_records[result_records_filled]["or_set_idx"] = order_settings_index
                        strategy_result_records[result_records_filled]["total_trades"] = wins_and_losses_array.size
                        strategy_result_records[result_records_filled]["gains_pct"] = gains_pct
                        strategy_result_records[result_records_filled]["win_rate"] = win_rate
                        strategy_result_records[result_records_filled]["to_the_upside"] = to_the_upside
                        strategy_result_records[result_records_filled]["total_pnl"] = total_pnl
                        strategy_result_records[result_records_filled]["ending_eq"] = order.equity

                        result_records_filled += 1
        info_logger.info(f"Starting New Loop\n\n")

    return pd.DataFrame(strategy_result_records[:result_records_filled]).sort_values(
        by=["to_the_upside", "gains_pct"],
        ascending=False,
        ignore_index=True,
    )


def order_records_bt(
    starting_equity: float,
    os_cart_arrays: OrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    strategy: Strategy,
    candles: np.array,
    backtest_results: pd.DataFrame,
    backtest_index: int,
):
    ind_or_indexes = backtest_results.iloc[backtest_index][["ind_set_idx", "or_set_idx"]].astype(int).values
    ind_set_index = ind_or_indexes[0]
    or_set_index = ind_or_indexes[1]
    total_bars = candles.shape[0]
    order_records = np.empty(total_bars, dtype=or_dt)
    total_order_records_filled = 0

    if strategy.candle_processing_mode == CandleProcessingType.Backtest:
        calc_starting_bar = starting_bar_backtest
    else:
        calc_starting_bar = starting_bar_real

    strategy.set_indicator_settings(indicator_settings_index=ind_set_index)

    order_settings = get_order_setting(
        order_settings_index=or_set_index,
        os_cart_arrays=os_cart_arrays,
    )

    order = Order.instantiate(
        equity=starting_equity,
        order_settings=order_settings,
        exchange_settings=exchange_settings,
        long_or_short=order_settings.long_or_short,
        order_records=order_records,
        total_order_records_filled=total_order_records_filled,
    )

    info_logger.debug(f"Created Order class")

    starting_bar = calc_starting_bar(order_settings.num_candles)

    for bar_index in range(starting_bar, total_bars):
        info_logger.debug(
            f"ind_idx={ind_set_index:,} os_idx={or_set_index:,} b_idx={bar_index} timestamp={pd.to_datetime(candles['timestamp'][bar_index], unit='ms')}"
        )
        if order.position_size_usd > 0:
            try:
                order.check_stop_loss_hit(current_candle=candles[bar_index])
                order.check_liq_hit(current_candle=candles[bar_index])
                order.check_take_profit_hit(
                    current_candle=candles[bar_index],
                    exit_signal=strategy.current_exit_signals[bar_index],
                )
                order.check_move_stop_loss_to_be(bar_index=bar_index, candles=candles)
                order.check_move_trailing_stop_loss(bar_index=bar_index, candles=candles)
            except RejectedOrder as e:
                info_logger.warning(f"RejectedOrder -> {e.msg}")
                pass
            except DecreasePosition as e:
                order.decrease_position(
                    order_status=e.order_status,
                    exit_price=e.exit_price,
                    exit_fee_pct=e.exit_fee_pct,
                    bar_index=bar_index,
                    timestamp=candles["timestamp"][bar_index],
                    indicator_settings_index=ind_set_index,
                    order_settings_index=or_set_index,
                )
            except MoveStopLoss as e:
                order.move_stop_loss(
                    sl_price=e.sl_price,
                    order_status=e.order_status,
                    bar_index=bar_index,
                    timestamp=candles["timestamp"][bar_index],
                    indicator_settings_index=ind_set_index,
                    order_settings_index=or_set_index,
                )
            except Exception as e:
                info_logger.error(f"Exception placing order -> {e}")
                raise Exception(f"Exception placing order -> {e}")
        strategy.create_indicator(bar_index=bar_index, starting_bar=starting_bar)
        if strategy.evaluate():  # add in that we are also not at max entry amount
            try:
                order.calculate_stop_loss(bar_index=bar_index, candles=candles)
                order.calculate_increase_posotion(entry_price=candles["close"][bar_index])
                order.calculate_leverage()
                order.calculate_take_profit()
                order.or_filler(
                    order_result=OrderResult(
                        indicator_settings_index=ind_set_index,
                        order_settings_index=or_set_index,
                        bar_index=bar_index + 1,
                        timestamp=candles["timestamp"][bar_index + 1],
                        available_balance=order.available_balance,
                        cash_borrowed=order.cash_borrowed,
                        cash_used=order.cash_used,
                        average_entry=order.average_entry,
                        leverage=order.leverage,
                        liq_price=order.liq_price,
                        order_status=order.order_status,
                        possible_loss=order.possible_loss,
                        entry_size_usd=order.entry_size_usd,
                        entry_price=order.entry_price,
                        position_size_usd=order.position_size_usd,
                        sl_pct=order.sl_pct,
                        sl_price=order.sl_price,
                        tp_pct=order.tp_pct,
                        tp_price=order.tp_price,
                    )
                )
            except RejectedOrder as e:
                info_logger.warning(f"RejectedOrder -> {e.msg}")
                pass
            except Exception as e:
                info_logger.error(f"Exception placing order -> {e}")
                raise Exception(f"Exception placing order -> {e}")

    order_records = order.order_records
    total_order_records_filled = order.total_order_records_filled

    return pd.DataFrame(order_records[:total_order_records_filled])
