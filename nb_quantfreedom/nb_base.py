import numpy as np
import pandas as pd
from nb_quantfreedom.nb_helper_funcs import get_order_setting, get_to_the_upside_nb
from nb_quantfreedom.np_enums import (
    BacktestSettings,
    CandleBodyType,
    CandleProcessingType,
    ExchangeSettings,
    IncreasePositionType,
    LeverageStrategyType,
    LongOrShortType,
    OrderResult,
    OrderSettingsArrays,
    OrderStatus,
    PriceGetterType,
    RejectedOrder,
    SLToBeZeroOrEntryType,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
    TestStaticOrderSettings,
    strat_df_array_dt,
    strat_records_dt,
)
from nb_quantfreedom.nb_order_handler.nb_increase_position import (
    nb_IncreasePosition,
    nb_Long_RPAandSLB,
    nb_Long_SEP,
    nb_StartBarBacktest,
    nb_StartBarReal,
)
from nb_quantfreedom.nb_order_handler.nb_leverage import (
    nb_Leverage,
    nb_Long_CalcDynamicLeverage,
    nb_Long_Leverage,
    nb_Long_SetStaticLeverage,
)
from nb_quantfreedom.nb_order_handler.nb_price_getter import nb_GetMaxPrice, nb_GetMinPrice
from nb_quantfreedom.nb_order_handler.nb_stop_loss import (
    nb_Long_SLCandleBody,
    nb_Long_SLToEntry,
    nb_Long_SLToZero,
    nb_Long_StopLoss,
    nb_StopLoss,
)
from nb_quantfreedom.nb_order_handler.nb_take_profit import (
    nb_Long_TPHitProvided,
    nb_Long_TPHitReg,
    nb_Long_TPRiskReward,
    nb_TakeProfit,
)
from nb_quantfreedom.strategies.strategy import Strategy


def starting_bar_backtest(num_candles: int):
    return 0


def starting_bar_real(num_candles: int):
    return num_candles - 1


def backtest_df_only(
    starting_equity: float,
    os_cart_arrays: OrderSettingsArrays,
    static_os: TestStaticOrderSettings,
    backtest_settings: BacktestSettings,
    exchange_settings: ExchangeSettings,
    strategy: Strategy,
    candles: np.array,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if static_os.long_or_short == LongOrShortType.Long:
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
            sl_calc = nb_Long_SLCandleBody()
            sl_hit_checker = nb_Long_StopLoss()
            if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
                sl_price_getter = nb_GetMinPrice()
            elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
                sl_price_getter = nb_GetMaxPrice()
        elif static_os.stop_loss_type == StopLossStrategyType.Nothing:
            sl_calc = nb_StopLoss()
            sl_price_getter = nb_StopLoss()

        # setting up stop loss break even checker
        if static_os.sl_to_break_even:
            move_sl_to_be_checker = nb_Long_StopLoss()
            if static_os.pg_min_max_sl_be == PriceGetterType.Min:
                sl_to_be_price_getter = nb_GetMinPrice()
            elif static_os.pg_min_max_sl_be == PriceGetterType.Max:
                sl_to_be_price_getter = nb_GetMaxPrice()
        else:
            move_sl_to_be_checker = nb_StopLoss()
            sl_to_be_price_getter = nb_StopLoss()

        # setting up stop loss break even checker
        if static_os.trail_sl:
            move_tsl_checker = nb_Long_StopLoss()
            if static_os.pg_min_max_tsl == PriceGetterType.Min:
                tsl_price_getter = nb_GetMinPrice()
            if static_os.pg_min_max_tsl == PriceGetterType.Min:
                tsl_price_getter = nb_GetMinPrice()
        else:
            move_tsl_checker = nb_StopLoss()
            tsl_price_getter = nb_StopLoss()

        # setting up stop loss be zero or entry
        if static_os.sl_to_be_zero_or_entry_type == SLToBeZeroOrEntryType.Nothing:
            set_sl_to_be_z_or_e = nb_StopLoss()
        elif static_os.sl_to_be_zero_or_entry_type == SLToBeZeroOrEntryType.ZeroLoss:
            set_sl_to_be_z_or_e = nb_Long_SLToZero()
        elif static_os.sl_to_be_zero_or_entry_type == SLToBeZeroOrEntryType.AverageEntry:
            set_sl_to_be_z_or_e = nb_Long_SLToEntry()

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
                calc_increase_pos = nb_Long_RPAandSLB()

            elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
                calc_increase_pos = nb_Long_SEP()

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
            calc_leverage = nb_Long_CalcDynamicLeverage()
        else:
            calc_leverage = nb_Long_SetStaticLeverage()

        liq_hit_checker = nb_Long_Leverage()
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
            tp_calculator = nb_Long_TPRiskReward()
            tp_hit_checker = nb_Long_TPHitReg()
        elif static_os.take_profit_type == TakeProfitStrategyType.Provided:
            tp_calculator = nb_TakeProfit()
            tp_hit_checker = nb_Long_TPHitProvided()
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


def nb_run_backtest(
    backtest_settings: BacktestSettings,
    calc_starting_bar: nb_IncreasePosition,
    candles: np.array,
    exchange_settings: ExchangeSettings,
    exit_fee_pct: float,
    liq_hit_checker: nb_Leverage,
    os_cart_arrays: OrderSettingsArrays,
    sl_hit_checker: nb_StopLoss,
    starting_equity: float,
    strategy: Strategy,
    total_bars: int,
    total_indicator_settings: int,
    total_order_settings: int,
    tp_hit_checker: nb_TakeProfit,
):
    market_fee_pct = exchange_settings.market_fee_pct

    array_size = int(total_indicator_settings * total_order_settings / backtest_settings.divide_records_array_size_by)

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )

    result_records_filled = 0

    strat_records = np.empty(int(total_bars / 2), dtype=strat_records_dt)

    for indicator_settings_index in range(total_indicator_settings):
        print(f"Indicator settings index = {indicator_settings_index:,}")
        strategy.set_indicator_settings(indicator_settings_index=indicator_settings_index)

        for order_settings_index in range(total_order_settings):
            print(f"Order settings index = {order_settings_index:,}")
            order_settings = get_order_setting(
                order_settings_index=order_settings_index,
                os_cart_arrays=os_cart_arrays,
            )

            print(f"Created Order class")

            starting_bar = calc_starting_bar(order_settings.num_candles)

            order_results = OrderResult(
                indicator_settings_index=indicator_settings_index,
                order_settings_index=order_settings_index,
                bar_index=bar_index,
                timestamp=0,
                equity=starting_equity,
                available_balance=starting_equity,
                cash_borrowed=0.0,
                cash_used=0.0,
                average_entry=0.0,
                fees_paid=0.0,
                leverage=1.0,
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

            # entries loop
            for bar_index in range(starting_bar, total_bars):
                print(
                    f"ind_idx={indicator_settings_index:,} os_idx={order_settings_index:,} b_idx={bar_index} timestamp={pd.to_datetime(candles[bar_index, CandleBodyType.Timestamp], unit='ms')}"
                )
                if order_results.position_size_usd > 0:
                    try:
                        sl_hit_checker.check_stop_loss_hit(
                            current_candle=candles[bar_index, :],
                            exit_fee_pct=market_fee_pct,
                            sl_price=order_results.sl_price,
                        )
                        liq_hit_checker.check_liq_hit(
                            current_candle=candles[bar_index, :],
                            exit_fee_pct=market_fee_pct,
                            liq_price=order_results.liq_price,
                        )

                        tp_hit_checker.check_tp_hit(
                            current_candle=candles[bar_index, :],
                            exit_fee_pct=exit_fee_pct,
                            tp_price=order_results.tp_price,
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
                        print(f"Exception placing order -> {e}")
                        raise Exception(f"Exception placing order -> {e}")
                strategy.create_indicator(bar_index=bar_index, starting_bar=starting_bar)
                if strategy.evaluate():  # add in that we are also not at max entry amount
                    try:
                        order.calculate_stop_loss(bar_index=bar_index, candles=candles)
                        order.calculate_increase_posotion(entry_price=candles["close"][bar_index])
                        order.calculate_leverage()
                        order.calculate_take_profit()

                    except RejectedOrder as e:
                        print(f"RejectedOrder -> {e.msg}")
                        pass
                    except Exception as e:
                        print(f"Exception placing order -> {e}")
                        raise Exception(f"Exception placing order -> {e}")
            # Checking if gains
            gains_pct = round(((order.equity - starting_equity) / starting_equity) * 100, 2)
            print(f"Starting eq={starting_equity} Ending eq={order.equity} gains pct={gains_pct}")
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
        print(f"Starting New Loop\n\n")

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
