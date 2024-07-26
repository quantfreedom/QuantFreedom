import numpy as np
from os.path import join, abspath

from logging import getLogger

from quantfreedom.core.enums import (
    DecreasePosition,
    FootprintCandlesTuple,
    OrderStatus,
    RejectedOrder,
    ExchangeSettings,
    StaticOrderSettings,
    or_dt,
)

from quantfreedom.grid.grid_order_handler.grid_order import GridOrderHandler
from quantfreedom.grid.grid_order_handler.grid_leverage.grid_lev_exec import Grid_Lev_Funcs
from quantfreedom.grid.grid_order_handler.grid_stop_loss.grid_sl_exec import Grid_SL_Funcs
from quantfreedom.grid.grid_order_handler.grid_decrease_position.grid_dp_exec import Grid_DP_Funcs
from quantfreedom.helpers.custom_logger import set_loggers


logger = getLogger()


def grid_backtest(
    candles: FootprintCandlesTuple,
    price_pct: float,
    pct_account: float,
    leverage: float,
    equity: float = 1000,
    exchange_settings_tuple: ExchangeSettings = None,
    static_os_tuple: StaticOrderSettings = None,
):
    set_loggers(disable_logger=False, log_level="DEBUG", log_path=abspath(join(abspath(""), "..")))
    price_pct /= 100
    pct_account /= 100

    position_size = 0
    average_entry = 0
    cash_borrowed = 0
    cash_used = 0
    avaliable_balance = equity

    closing_prices = candles.candle_close_prices
    low_prices = candles.candle_low_prices
    high_prices = candles.candle_high_prices
    open_prices = candles.candle_open_prices
    datetimes = candles.candle_open_datetimes

    grid_order_handler = GridOrderHandler()

    grid_order_handler.reset_grid_order_variables(equity=equity)

    pnl_array = np.full_like(closing_prices, np.nan)
    ae_buy_array = np.full_like(closing_prices, np.nan)
    ae_sell_array = np.full_like(closing_prices, np.nan)
    ps_array = np.full_like(closing_prices, np.nan)

    sell_order = closing_prices[0] + (closing_prices[0] * price_pct)
    sell_signals = np.full_like(closing_prices, np.nan)

    buy_order = closing_prices[0] - (closing_prices[0] * price_pct)
    buy_signals = np.full_like(closing_prices, np.nan)

    total_bars = candles.candle_open_timestamps.size
    or_filled = 0
    order_records = np.empty(shape=int(total_bars / 3), dtype=or_dt)

    for bar_index in range(1, closing_prices.size):
        logger.debug(f"Bar Index: {bar_index}")
        try:
            if position_size > 0:  # in a long position

                current_candle = grid_order_handler.helpers.get_current_candle(
                    bar_index=bar_index,
                    candles=candles,
                )

                get_pnl = Grid_DP_Funcs.long_get_pnl

                grid_order_handler.check_stop_loss_hit(
                    check_sl_hit_bool=Grid_SL_Funcs.long_check_sl_hit_bool,
                    current_candle=current_candle,
                )

                grid_order_handler.check_liq_hit(
                    check_liq_hit_bool=Grid_Lev_Funcs.long_check_liq_hit_bool,
                    current_candle=current_candle,
                )

            elif position_size < 0:

                current_candle = grid_order_handler.helpers.get_current_candle(
                    bar_index=bar_index,
                    candles=candles,
                )

                get_pnl = Grid_DP_Funcs.short_get_pnl

                grid_order_handler.check_stop_loss_hit(
                    check_sl_hit_bool=Grid_SL_Funcs.short_check_sl_hit_bool,
                    current_candle=current_candle,
                )

                grid_order_handler.check_liq_hit(
                    current_candle=current_candle,
                    liq_hit_bool_exec=Grid_Lev_Funcs.short_check_liq_hit_bool,
                )

        except DecreasePosition as dp:
            (
                equity,
                fees_paid,
                realized_pnl,
            ) = grid_order_handler.calculate_decrease_position(
                cur_datetime=candles.candle_open_datetimes[bar_index],
                exit_fee=grid_order_handler.market_fee_pct,
                exit_price=dp.exit_price,
                exit_size_asset=abs(grid_order_handler.position_size_asset),
                equity=grid_order_handler.equity,
                get_pnl=get_pnl,
                order_status=dp.order_status,
            )

            grid_order_handler.helpers.fill_order_record_exit(
                bar_index=bar_index,
                set_idx=0,
                order_records=order_records[or_filled],
                order_status=dp.order_status,
                timestamp=current_candle.open_timestamp,
                equity=equity,
                fees_paid=fees_paid,
                realized_pnl=realized_pnl,
                sl_price=dp.sl_price,
                liq_price=dp.liq_price,
            )

            or_filled += 1
            logger.debug(f"Filled decrease postiion order records for {OrderStatus._fields[dp.order_status]}")

            grid_order_handler.reset_grid_order_variables(
                equity=equity,
            )
            logger.debug("reset order variables")
        try:
            if low_prices[bar_index] <= buy_order:
                order_size = equity * pct_account
                temp_pos_size = position_size + order_size

                buy_signals[bar_index] = buy_order
                if position_size >= 0:
                    # adding to long position
                    get_bankruptcy_price = Grid_Lev_Funcs.long_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.long_get_liq_price

                    average_entry = grid_order_handler.calculate_average_entry(
                        entry_price=buy_order,
                        order_size=order_size,
                    )
                    ae_buy_array[bar_index] = average_entry
                    entry_price = buy_order
                    entry_size_asset = order_size / average_entry
                    entry_size_usd = order_size
                    equity = grid_order_handler.equity
                    fees_paid = np.nan
                    realized_pnl = np.nan
                    exit_price = np.nan

                elif temp_pos_size >= 0 and position_size <= 0:
                    # switch from short to long
                    get_bankruptcy_price = Grid_Lev_Funcs.long_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.long_get_liq_price

                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=buy_order,
                        exit_fee=grid_order_handler.limit_fee_pct,
                        exit_size_asset=abs(position_size) / average_entry,
                        equity=equity,
                        order_status=OrderStatus.TakeProfitFilled,
                        pnl_exec=Grid_DP_Exec_Tuple.short_pnl_exec,
                    )

                    average_entry = buy_order
                    entry_price = buy_order
                    entry_size_asset = order_size / average_entry
                    entry_size_usd = order_size
                    exit_price = buy_order

                    ae_buy_array[bar_index] = average_entry

                elif temp_pos_size < 0:
                    # tp on short
                    get_bankruptcy_price = Grid_Lev_Funcs.short_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.short_get_liq_price

                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=buy_order,
                        exit_fee=grid_order_handler.limit_fee_pct,
                        exit_size_asset=order_size / average_entry,
                        equity=equity,
                        order_status=OrderStatus.TakeProfitFilled,
                        pnl_exec=Grid_DP_Exec_Tuple.short_pnl_exec,
                    )
                    average_entry = grid_order_handler.average_entry
                    entry_price = np.nan
                    entry_size_asset = np.nan
                    entry_size_usd = np.nan
                    exit_price = buy_order

                position_size = temp_pos_size

                (
                    available_balance,
                    cash_borrowed,
                    cash_used,
                    liq_price,
                ) = grid_order_handler.calculate_liquidation_price(
                    average_entry=average_entry,
                    get_bankruptcy_price=get_bankruptcy_price,
                    get_liq_price=get_liq_price,
                    leverage=leverage,
                    og_available_balance=avaliable_balance,
                    og_cash_borrowed=cash_borrowed,
                    og_cash_used=cash_used,
                    position_size_asset=abs(position_size) / average_entry,
                    position_size_usd=abs(position_size),
                )

                grid_order_handler.set_grid_variables(
                    available_balance=available_balance,
                    average_entry=average_entry,
                    cash_borrowed=cash_borrowed,
                    cash_used=cash_used,
                    entry_price=entry_price,
                    entry_size_asset=entry_size_asset,
                    entry_size_usd=entry_size_usd,
                    equity=equity,
                    exit_price=exit_price,
                    fees_paid=fees_paid,
                    leverage=leverage,
                    liq_price=liq_price,
                    order_status=OrderStatus.EntryFilled,
                    position_size_asset=position_size / average_entry,
                    position_size_usd=position_size,
                    total_possible_loss=np.nan,
                    realized_pnl=np.nan,
                    sl_pct=np.nan,
                    sl_price=np.nan,
                    total_trades=np.nan,
                    tp_pct=np.nan,
                    tp_price=np.nan,
                )

                ps_array[bar_index] = position_size
                buy_order = closing_prices[bar_index] - (closing_prices[bar_index] * price_pct)
                sell_order = closing_prices[bar_index] + (closing_prices[bar_index] * price_pct)

            # elif high_prices[bar_index] >= sell_order:
            #     order_size = equity * pct_account
            #     temp_pos_size = position_size + -order_size

            #     sell_signals[bar_index] = sell_order

            #     if temp_pos_size > 0:
            #         # tp on long
            #         equity = calc_take_profit(
            #             average_entry=average_entry,
            #             equity=equity,
            #             bar_index=bar_index,
            #             limit_order=sell_order,
            #             order_size=order_size,
            #             pnl_array=pnl_array,
            #             tp_on_long_short="long",
            #         )

            #     elif temp_pos_size <= 0 and position_size >= 0:

            #         equity = calc_take_profit(
            #             average_entry=average_entry,
            #             equity=equity,
            #             bar_index=bar_index,
            #             limit_order=sell_order,
            #             order_size=position_size,
            #             pnl_array=pnl_array,
            #             tp_on_long_short="long",
            #         )
            #         average_entry = sell_order
            #         ae_sell_array[bar_index] = average_entry

            #     elif position_size <= 0:
            #         # adding to short position
            #         try:
            #             average_entry = (-position_size + order_size) / (
            #                 (-position_size / average_entry) + (order_size / sell_order)
            #             )
            #             ae_sell_array[bar_index] = average_entry

            #         except ZeroDivisionError:
            #             average_entry = sell_order
            #             ae_sell_array[bar_index] = average_entry

            #     position_size = temp_pos_size
            #     ps_array[bar_index] = position_size
            #     buy_order = closing_prices[bar_index] - (closing_prices[bar_index] * price_pct)
            #     sell_order = closing_prices[bar_index] + (closing_prices[bar_index] * price_pct)
        except RejectedOrder:
            pass
        except Exception as e:
            logger.error(f"Error: {e}")
            raise Exception(e)
