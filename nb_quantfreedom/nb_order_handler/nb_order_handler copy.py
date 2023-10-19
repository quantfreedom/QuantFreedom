from nb_quantfreedom.nb_enums import (
    CandleBodyType,
    IncreasePositionType,
    LeverageStrategyType,
    LongOrShortType,
    PriceGetterType,
    SLToBeZeroOrEntryType,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
)
from nb_quantfreedom.nb_order_handler.nb_increase_position import nb_Long_RPAandSLB, nb_Long_SEP
from nb_quantfreedom.nb_order_handler.nb_leverage import nb_CalcDynamicLeverage, nb_SetStaticLeverage
from nb_quantfreedom.nb_order_handler.nb_price_getter import nb_GetMaxPrice, nb_GetMinPrice
from nb_quantfreedom.nb_order_handler.nb_stop_loss import (
    nb_Long_SLCandleBody,
    nb_Long_SLToEntry,
    nb_Long_SLToZero,
    nb_Long_StopLoss,
    nb_StopLoss,
)
from nb_quantfreedom.nb_order_handler.nb_take_profit import (
    nb_TPHitProvided,
    nb_TPHitReg,
    nb_TPRiskReward,
    nb_TakeProfit,
)


def set_classes(
    increase_position_type: IncreasePositionType,
    leverage_type: LeverageStrategyType,
    long_or_short: LongOrShortType,
    pg_min_or_max_sl_based_cb: PriceGetterType,
    pg_min_or_max_sl_be: PriceGetterType,
    pg_min_or_max_tsl: PriceGetterType,
    sl_to_break_even: bool,
    sl_to_be_zero_or_entry_type: SLToBeZeroOrEntryType,
    stop_loss_type: StopLossStrategyType,
    take_profit_type: TakeProfitStrategyType,
    trail_sl: bool,
    tp_fee_type: TakeProfitFeeType,
):
    if long_or_short == LongOrShortType.Long:
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
        if stop_loss_type == StopLossStrategyType.SLBasedOnCandleBody:
            sl_calc = nb_Long_SLCandleBody()
            sl_hit_checker = nb_Long_StopLoss()
            if pg_min_or_max_sl_based_cb == PriceGetterType.Min:
                sl_price_getter = nb_GetMinPrice()
            elif pg_min_or_max_sl_based_cb == PriceGetterType.Max:
                sl_price_getter = nb_GetMaxPrice()
        elif stop_loss_type == StopLossStrategyType.Nothing:
            sl_calc = nb_StopLoss()
            sl_price_getter = nb_StopLoss()

        # setting up stop loss break even checker
        if sl_to_break_even:
            move_sl_to_be_checker = nb_Long_StopLoss()
            if pg_min_or_max_sl_be == PriceGetterType.Min:
                sl_to_be_price_getter = nb_GetMinPrice()
            elif pg_min_or_max_sl_be == PriceGetterType.Max:
                sl_to_be_price_getter = nb_GetMaxPrice()
        else:
            move_sl_to_be_checker = nb_StopLoss()
            sl_to_be_price_getter = nb_StopLoss()

        # setting up stop loss break even checker
        if trail_sl:
            move_tsl_checker = nb_Long_StopLoss()
            if pg_min_or_max_tsl == PriceGetterType.Min:
                tsl_price_getter = nb_GetMinPrice()
            if pg_min_or_max_tsl == PriceGetterType.Min:
                tsl_price_getter = nb_GetMinPrice()
        else:
            move_tsl_checker = nb_StopLoss()
            tsl_price_getter = nb_StopLoss()

        # setting up stop loss be zero or entry
        if sl_to_be_zero_or_entry_type == SLToBeZeroOrEntryType.Nothing:
            set_sl_to_be_z_or_e = nb_StopLoss()
        elif sl_to_be_zero_or_entry_type == SLToBeZeroOrEntryType.ZeroLoss:
            set_sl_to_be_z_or_e = nb_Long_SLToZero()
        elif sl_to_be_zero_or_entry_type == SLToBeZeroOrEntryType.AverageEntry:
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

        if stop_loss_type == StopLossStrategyType.SLBasedOnCandleBody:
            if increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                calc_increase_pos = nb_Long_RPAandSLB()

            elif increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
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

        if leverage_type == LeverageStrategyType.Dynamic:
            calc_leverage = nb_CalcDynamicLeverage()
        else:
            calc_leverage = nb_SetStaticLeverage()

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

        if take_profit_type == TakeProfitStrategyType.RiskReward:
            take_profit_calculator = nb_TPRiskReward()
            tp_checker = nb_TPHitReg()
        elif take_profit_type == TakeProfitStrategyType.Provided:
            take_profit_calculator = nb_TakeProfit()
            tp_checker = nb_TPHitProvided()

        if tp_fee_type == TakeProfitFeeType.Market:
            exit_fee_pct = 0.0003
        else:
            exit_fee_pct = 0.0009

    nb_simulate_backtest(candles=candle)
