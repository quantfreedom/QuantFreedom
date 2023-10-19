import numpy as np
import pandas as pd
from numba import njit

from nb_quantfreedom.nb_helper_funcs import get_to_the_upside_nb, nb_get_dos
from nb_quantfreedom.nb_enums import (
    BacktestSettings,
    CandleBodyType,
    CandleProcessingType,
    DecreasePosition,
    DynamicOrderSettingsArrays,
    ExchangeSettings,
    IncreasePositionType,
    LeverageStrategyType,
    LongOrShortType,
    MoveStopLoss,
    OrderResult,
    OrderSettingsArrays,
    OrderStatus,
    PriceGetterType,
    RejectedOrder,
    SLToBeZeroOrEntryType,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
    StaticOrderSettings,
    strat_df_array_dt,
)
from nb_quantfreedom.nb_order_handler.nb_decrease_position import nb_DecreasePosition, nb_Long_DP
from nb_quantfreedom.nb_order_handler.nb_increase_position import (
    nb_IncreasePosition,
    nb_Long_RPAandSLB,
    nb_Long_SEP,
    nb_StartBarBacktest,
    nb_StartBarReal,
)
from nb_quantfreedom.nb_order_handler.nb_leverage import (
    nb_Leverage,
    nb_Long_DLev,
    nb_Long_Leverage,
    nb_Long_SLev,
)
from nb_quantfreedom.nb_order_handler.nb_class_helpers import (
    nb_GetMaxPrice,
    nb_GetMinPrice,
    nb_Long_SLToEntry,
    nb_Long_SLToZero,
    nb_PriceGetter,
    nb_ZeroOrEntry,
)

from nb_quantfreedom.nb_order_handler.nb_stop_loss import (
    nb_Long_SLBCB,
    nb_Long_StopLoss,
    nb_MoveSL,
    nb_StopLoss,
)
from nb_quantfreedom.nb_order_handler.nb_take_profit import (
    nb_Long_RR,
    nb_Long_TPHitReg,
    nb_TakeProfit,
)
from nb_quantfreedom.strategies.strategy import Strategy


def backtest_df_only(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_cart_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    starting_equity: float,
    static_os: StaticOrderSettings,
    strategy: Strategy,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if static_os.long_or_short == LongOrShortType.Long:
        # Decrease Position
        dec_pos_calculator = nb_Long_DP()

        """
        #########################################
        #########################################
        #########################################
                        Stop Loss
                        Stop Loss
                        Stop Loss
        #########################################
        #########################################
        #########################################
        """

        # setting up stop loss calulator
        if static_os.stop_loss_type == StopLossStrategyType.SLBasedOnCandleBody:
            sl_calculator = nb_Long_SLBCB()
            checker_sl_hit = nb_Long_StopLoss()
            if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
                sl_bcb_price_getter = nb_GetMinPrice()
            elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
                sl_bcb_price_getter = nb_GetMaxPrice()
        elif static_os.stop_loss_type == StopLossStrategyType.Nothing:
            sl_calculator = nb_StopLoss()
            sl_bcb_price_getter = nb_StopLoss()

        # setting up stop loss break even checker
        if static_os.sl_to_be:
            checker_sl_to_be = nb_Long_StopLoss()
            # setting up stop loss be zero or entry
            if static_os.sl_to_be_ze_type == SLToBeZeroOrEntryType.ZeroLoss:
                set_z_e = nb_Long_SLToZero()
            elif static_os.sl_to_be_ze_type == SLToBeZeroOrEntryType.AverageEntry:
                set_z_e = nb_Long_SLToEntry()
        else:
            checker_sl_to_be = nb_StopLoss()
            set_z_e = nb_ZeroOrEntry()

        # setting up stop loss break even checker
        if static_os.trail_sl:
            checker_tsl = nb_Long_StopLoss()
        else:
            checker_tsl = nb_StopLoss()

        if static_os.trail_sl or static_os.sl_to_break_even:
            sl_mover = nb_MoveSL()
        else:
            sl_mover = nb_StopLoss()

        """
        #########################################
        #########################################
        #########################################
                    Increase position
                    Increase position
                    Increase position
        #########################################
        #########################################
        #########################################
        """

        if static_os.stop_loss_type == StopLossStrategyType.SLBasedOnCandleBody:
            if static_os.increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                inc_pos_calculator = nb_Long_RPAandSLB()

            elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
                inc_pos_calculator = nb_Long_SEP()

        """
        #########################################
        #########################################
        #########################################
                        Leverage
                        Leverage
                        Leverage
        #########################################
        #########################################
        #########################################
        """

        if static_os.leverage_type == LeverageStrategyType.Dynamic:
            lev_calculator = nb_Long_DLev()
        else:
            lev_calculator = nb_Long_SLev()

        checker_liq_hit = nb_Long_Leverage()
        """
        #########################################
        #########################################
        #########################################
                        Take Profit
                        Take Profit
                        Take Profit
        #########################################
        #########################################
        #########################################
        """

        if static_os.take_profit_type == TakeProfitStrategyType.RiskReward:
            tp_calculator = nb_Long_RR()
            checker_tp_hit = nb_Long_TPHitReg()
        elif static_os.take_profit_type == TakeProfitStrategyType.Provided:
            pass
    """
    #########################################
    #########################################
    #########################################
                Other Settings
                Other Settings
                Other Settings
    #########################################
    #########################################
    #########################################
    """
    if strategy.candle_processing_mode == CandleProcessingType.Backtest:
        calc_starting_bar = nb_StartBarBacktest()
    else:
        calc_starting_bar = nb_StartBarReal()

    if static_os.tp_fee_type == TakeProfitFeeType.Market:
        exit_fee_pct = exchange_settings.market_fee_pct
    else:
        exit_fee_pct = exchange_settings.limit_fee_pct
    """
    #########################################
    #########################################
    #########################################
                End User Setup
                End User Setup
                End User Setup
    #########################################
    #########################################
    #########################################
    """
    # Creating Settings Vars
    total_order_settings = dos_cart_arrays[0].size

    total_indicator_settings = strategy.indicator_cart_product[0].size

    total_bars = candles.size

    # Printing out total numbers of things
    print("Starting the backtest now ... and also here are some stats for your backtest.\n")
    print(f"Total indicator settings to test: {total_indicator_settings:,}")
    print(f"Total order settings to test: {total_order_settings:,}")
    print(f"Total combinations of settings to test: {total_indicator_settings * total_order_settings:,}")
    print(f"\nTotal candles: {total_bars:,}")
    print(f"Total candles to test: {total_indicator_settings * total_order_settings * total_bars:,}")

    strategy_result_records = nb_run_backtest(
        backtest_settings=backtest_settings,
        calc_starting_bar=calc_starting_bar,
        candles=candles,
        checker_liq_hit=checker_liq_hit,
        checker_sl_hit=checker_sl_hit,
        checker_sl_to_be=checker_sl_to_be,
        checker_tp_hit=checker_tp_hit,
        checker_tsl=checker_tsl,
        dec_pos_calculator=dec_pos_calculator,
        dos_cart_arrays=dos_cart_arrays,
        exchange_settings=exchange_settings,
        exit_fee_pct=exit_fee_pct,
        inc_pos_calculator=inc_pos_calculator,
        lev_calculator=lev_calculator,
        set_z_e=set_z_e,
        sl_bcb_price_getter=sl_bcb_price_getter,
        sl_calculator=sl_calculator,
        sl_mover=sl_mover,
        starting_equity=starting_equity,
        strategy=strategy,
        total_bars=total_bars,
        total_indicator_settings=total_indicator_settings,
        total_order_settings=total_order_settings,
        tp_calculator=tp_calculator,
    )
    return pd.DataFrame(strategy_result_records).sort_values(
        by=["to_the_upside", "gains_pct"],
        ascending=False,
        ignore_index=True,
    )


@njit(cache=True)
def nb_run_backtest(
    backtest_settings: BacktestSettings,
    calc_starting_bar: nb_IncreasePosition,
    candles: np.array,
    checker_liq_hit: nb_Leverage,
    checker_sl_hit: nb_StopLoss,
    checker_sl_to_be: nb_StopLoss,
    checker_tp_hit: nb_TakeProfit,
    checker_tsl: nb_StopLoss,
    dec_pos_calculator: nb_DecreasePosition,
    dos_cart_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    exit_fee_pct: float,
    inc_pos_calculator: nb_IncreasePosition,
    lev_calculator: nb_Leverage,
    set_z_e: nb_ZeroOrEntry,
    sl_bcb_price_getter: nb_PriceGetter,
    sl_calculator: nb_StopLoss,
    sl_mover: nb_StopLoss,
    starting_equity: float,
    strategy: Strategy,
    total_bars: int,
    total_indicator_settings: int,
    total_order_settings: int,
    tp_calculator: nb_TakeProfit,
):
    market_fee_pct = exchange_settings.market_fee_pct
    price_tick_step = exchange_settings.price_tick_step
    asset_tick_step = exchange_settings.asset_tick_step
    min_asset_size = exchange_settings.min_asset_size
    max_asset_size = exchange_settings.max_asset_size
    max_leverage = exchange_settings.max_leverage
    mmr_pct = exchange_settings.mmr_pct

    array_size = int(total_indicator_settings * total_order_settings / backtest_settings.divide_records_array_size_by)

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )
    result_records_filled = 0

    for indicator_settings_index in range(total_indicator_settings):
        print(f"Indicator settings index = {indicator_settings_index:,}")
        strategy.set_indicator_settings(indicator_settings_index=indicator_settings_index)

        for dos_index in range(total_order_settings):
            print(f"Order settings index = {dos_index:,}")
            dynamic_order_settings = nb_get_dos(
                dos_cart_arrays=dos_cart_arrays,
                dos_index=dos_index,
            )

            print(f"Created Order class")

            starting_bar = calc_starting_bar(dynamic_order_settings.num_candles)

            order_result = OrderResult(
                indicator_settings_index=-1,
                dos_index=-1,
                bar_index=-1,
                timestamp=-1,
                equity=starting_equity,
                available_balance=starting_equity,
                cash_borrowed=0.0,
                cash_used=0.0,
                average_entry=0.0,
                can_move_sl_to_be=False,
                fees_paid=0.0,
                leverage=0.0,
                liq_price=0.0,
                order_status=OrderStatus.Nothing,
                possible_loss=0.0,
                entry_size_asset=0.0,
                entry_size_usd=0.0,
                entry_price=0.0,
                exit_price=0.0,
                position_size_asset=0.0,
                position_size_usd=0.0,
                realized_pnl=0.0,
                sl_pct=0.0,
                sl_price=0.0,
                total_trades=0,
                tp_pct=0.0,
                tp_price=0.0,
            )

            pnl_array = np.full(shape=array_size, fill_value=np.nan)
            filled_pnl_counter = 0

            total_fees_paid = 0

            # entries loop
            for bar_index in range(starting_bar, total_bars):
                print(
                    f"ind_idx={indicator_settings_index:,} os_idx={dos_index:,} b_idx={bar_index} timestamp={pd.to_datetime(candles[bar_index, CandleBodyType.Timestamp], unit='ms')}"
                )
                if order_result.position_size_usd > 0:
                    try:
                        checker_sl_hit.check_stop_loss_hit(
                            current_candle=candles[bar_index, :],
                            exit_fee_pct=market_fee_pct,
                            sl_price=order_result.sl_price,
                        )
                        checker_liq_hit.check_liq_hit(
                            current_candle=candles[bar_index, :],
                            exit_fee_pct=market_fee_pct,
                            liq_price=order_result.liq_price,
                        )

                        checker_tp_hit.check_tp_hit(
                            current_candle=candles[bar_index, :],
                            exit_fee_pct=exit_fee_pct,
                            tp_price=order_result.tp_price,
                        )

                        checker_sl_to_be.check_move_stop_loss_to_be(
                            average_entry=order_result.average_entry,
                            can_move_sl_to_be=order_result.can_move_sl_to_be,
                            candle_body_type=dynamic_order_settings.sl_to_be_cb_type,
                            current_candle=candles[bar_index, :],
                            set_z_e=set_z_e,
                            sl_price=order_result.sl_price,
                            sl_to_be_move_when_pct=dynamic_order_settings.sl_to_be_when_pct,
                            price_tick_step=price_tick_step,
                        )

                        checker_tsl.check_move_trailing_stop_loss(
                            average_entry=order_result.average_entry,
                            can_move_sl_to_be=order_result.can_move_sl_to_be,
                            candle_body_type=dynamic_order_settings.sl_to_be_cb_type,
                            current_candle=candles[bar_index, :],
                            price_tick_step=price_tick_step,
                            set_z_e=set_z_e,
                            sl_price=order_result.sl_price,
                            trail_sl_by_pct=dynamic_order_settings.trail_sl_by_pct,
                            trail_sl_when_pct=dynamic_order_settings.trail_sl_when_pct,
                        )
                    except RejectedOrder as e:
                        print(f"RejectedOrder -> {e.msg}")
                        pass
                    except MoveStopLoss as e:
                        order_result = sl_mover.move_stop_loss(
                            bar_index=bar_index,
                            can_move_sl_to_be=e.can_move_sl_to_be,
                            dos_index=dos_index,
                            indicator_settings_index=indicator_settings_index,
                            order_result=order_result,
                            order_status=e.order_status,
                            sl_price=e.sl_price,
                            timestamp=candles[bar_index : CandleBodyType.Timestamp],
                        )
                    except DecreasePosition as e:
                        equity, fees_paid, realized_pnl = dec_pos_calculator.decrease_position(
                            average_entry=order_result.average_entry,
                            equity=order_result.equity,
                            exit_fee_pct=e.exit_fee_pct,
                            exit_price=e.exit_price,
                            market_fee_pct=market_fee_pct,
                            order_status=e.order_status,
                            position_size_asset=order_result.position_size_asset,
                        )
                        # Fill pnl array
                        pnl_array[filled_pnl_counter] = realized_pnl
                        filled_pnl_counter += 1
                        total_fees_paid += fees_paid

                        # reset the order result
                        order_result = OrderResult(
                            indicator_settings_index=-1,
                            dos_index=-1,
                            bar_index=-1,
                            timestamp=-1,
                            equity=equity,
                            available_balance=equity,
                            cash_borrowed=0.0,
                            cash_used=0.0,
                            average_entry=0.0,
                            can_move_sl_to_be=False,
                            fees_paid=0.0,
                            leverage=0.0,
                            liq_price=0.0,
                            order_status=OrderStatus.Nothing,
                            possible_loss=0.0,
                            entry_size_asset=0.0,
                            entry_size_usd=0.0,
                            entry_price=0.0,
                            exit_price=0.0,
                            position_size_asset=0.0,
                            position_size_usd=0.0,
                            realized_pnl=0.0,
                            sl_pct=0.0,
                            sl_price=0.0,
                            total_trades=0,
                            tp_pct=0.0,
                            tp_price=0.0,
                        )
                    except Exception as e:
                        print(f"Exception placing order -> {e}")
                        raise Exception(f"Exception placing order -> {e}")
                strategy.create_indicator(bar_index=bar_index, starting_bar=starting_bar)  # TODO: this
                if strategy.evaluate():  # TODO: this and add in that we are also not at max entry amount
                    try:
                        sl_price = sl_calculator.calculate_stop_loss(
                            bar_index=bar_index,
                            candles=candles,
                            price_tick_step=price_tick_step,
                            sl_based_on_add_pct=dynamic_order_settings.sl_based_on_add_pct,
                            sl_based_on_lookback=dynamic_order_settings.sl_based_on_lookback,
                            sl_bcb_price_getter=sl_bcb_price_getter,
                            sl_bcb_type=dynamic_order_settings.sl_bcb_type,
                        )
                        (
                            average_entry,
                            entry_price,
                            entry_size_asset,
                            entry_size_usd,
                            position_size_asset,
                            position_size_usd,
                            possible_loss,
                            total_trades,
                            sl_pct,
                        ) = inc_pos_calculator.calculate_increase_posotion(
                            account_state_equity=order_result.equity,
                            asset_tick_step=asset_tick_step,
                            average_entry=order_result.average_entry,
                            entry_price=candles[bar_index, CandleBodyType.Close],
                            in_position=order_result.position_size_usd > 0,
                            market_fee_pct=market_fee_pct,
                            max_asset_size=max_asset_size,
                            max_equity_risk_pct=dynamic_order_settings.max_equity_risk_pct,
                            max_trades=dynamic_order_settings.max_trades,
                            min_asset_size=min_asset_size,
                            position_size_asset=order_result.position_size_asset,
                            position_size_usd=order_result.position_size_usd,
                            possible_loss=order_result.possible_loss,
                            price_tick_step=price_tick_step,
                            risk_account_pct_size=dynamic_order_settings.risk_account_pct_size,
                            sl_price=sl_price,
                            total_trades=order_result.total_trades,
                        )

                        (
                            available_balance,
                            can_move_sl_to_be,
                            cash_borrowed,
                            cash_used,
                            leverage,
                            liq_price,
                        ) = lev_calculator.calculate_leverage(
                            available_balance=order_result.available_balance,
                            average_entry=average_entry,
                            cash_borrowed=order_result.cash_borrowed,
                            cash_used=order_result.cash_used,
                            entry_size_usd=entry_size_usd,
                            max_leverage=max_leverage,
                            mmr_pct=mmr_pct,
                            sl_price=sl_price,
                            static_leverage=dynamic_order_settings.static_leverage,
                        )

                        (
                            can_move_sl_to_be,
                            tp_price,
                            tp_pct,
                        ) = tp_calculator.calculate_take_profit(
                            average_entry=average_entry,
                            market_fee_pct=market_fee_pct,
                            position_size_usd=position_size_usd,
                            possible_loss=possible_loss,
                            price_tick_step=price_tick_step,
                            risk_reward=dynamic_order_settings.risk_reward,
                            tp_fee_pct=exit_fee_pct,
                        )
                        order_result = OrderResult(
                            # where we are at
                            indicator_settings_index=indicator_settings_index,
                            dos_index=dos_index,
                            bar_index=bar_index + 1,  # put plus 1 because we need to place entry on next bar
                            timestamp=candles[bar_index + 1, CandleBodyType.Timestamp],
                            # account info
                            equity=order_result.equity,
                            available_balance=available_balance,
                            cash_borrowed=cash_borrowed,
                            cash_used=cash_used,
                            # order info
                            average_entry=average_entry,
                            can_move_sl_to_be=can_move_sl_to_be,
                            fees_paid=0.0,
                            leverage=leverage,
                            liq_price=liq_price,
                            order_status=OrderStatus.EntryFilled,
                            possible_loss=possible_loss,
                            entry_size_asset=entry_size_asset,
                            entry_size_usd=entry_size_usd,
                            entry_price=entry_price,
                            exit_price=0.0,
                            position_size_asset=position_size_asset,
                            position_size_usd=position_size_usd,
                            realized_pnl=0.0,
                            sl_pct=sl_pct,
                            sl_price=sl_price,
                            total_trades=total_trades,
                            tp_pct=tp_pct,
                            tp_price=tp_price,
                        )
                    except RejectedOrder as e:
                        print(f"RejectedOrder -> {e.msg}")
                        pass
                    except Exception as e:
                        print(f"Exception placing order -> {e}")
                        raise Exception(f"Exception placing order -> {e}")
            # Checking if gains
            gains_pct = round(((order_result.equity - starting_equity) / starting_equity) * 100, 2)
            print(f"Starting eq={starting_equity} Ending eq={order_result.equity} gains pct={gains_pct}")
            if gains_pct > backtest_settings.gains_pct_filter:
                wins_and_losses_array = pnl_array[~np.isnan(pnl_array["real_pnl"])]

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
                        strategy_result_records[result_records_filled]["dos_index"] = dos_index
                        strategy_result_records[result_records_filled]["total_trades"] = wins_and_losses_array.size
                        strategy_result_records[result_records_filled]["gains_pct"] = gains_pct
                        strategy_result_records[result_records_filled]["win_rate"] = win_rate
                        strategy_result_records[result_records_filled]["to_the_upside"] = to_the_upside
                        strategy_result_records[result_records_filled]["fees_paid"] = total_fees_paid
                        strategy_result_records[result_records_filled]["total_pnl"] = total_pnl
                        strategy_result_records[result_records_filled]["starting_eq"] = starting_equity
                        strategy_result_records[result_records_filled]["ending_eq"] = order_result.equity

                        result_records_filled += 1
        print(f"Starting New Loop\n\n")
    return strategy_result_records[:result_records_filled]


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

    print(f"Created Order class")

    starting_bar = calc_starting_bar(order_settings.num_candles)

    for bar_index in range(starting_bar, total_bars):
        print(
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
                print(f"RejectedOrder -> {e.msg}")
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
                print(f"Exception placing order -> {e}")
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
                print(f"RejectedOrder -> {e.msg}")
                pass
            except Exception as e:
                print(f"Exception placing order -> {e}")
                raise Exception(f"Exception placing order -> {e}")

    order_records = order.order_records
    total_order_records_filled = order.total_order_records_filled

    return pd.DataFrame(order_records[:total_order_records_filled])
