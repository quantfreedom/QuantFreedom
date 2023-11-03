import numpy as np

from quantfreedom.email_sender import EmailSender
from quantfreedom.enums import (
    CandleBodyType,
    DynamicOrderSettingsArrays,
    IncreasePositionType,
    LeverageStrategyType,
    LoggerFuncType,
    LongOrShortType,
    OrderPlacementType,
    PriceGetterType,
    StaticOrderSettings,
    StopLossStrategyType,
    StringerFuncType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
    ZeroOrEntryType,
)
from quantfreedom.exchanges.mufex_exchange.live_mufex import LiveMufex
from quantfreedom.helper_funcs import dos_cart_product, get_dos
from quantfreedom.live_mode import LiveTrading
from my_stuff import EmailSenderInfo, MufexTestKeys
from quantfreedom.strategies.strategy import (
    get_strategy_plot_filename,
    strat_evaluate,
    strat_get_current_ind_settings,
    strat_live_create_ind,
)

from quantfreedom.custom_logger import (
    file_candle_body_str,
    file_float_to_str,
    file_log_datetime,
    file_log_debug,
    file_log_error,
    file_log_info,
    file_log_warning,
    file_or_to_str,
    file_z_or_e_str,
    set_loggers,
)

if __name__ == "__main__":
    logger = []
    stringer = []

    set_loggers()
    logger.append(file_log_debug)
    logger.append(file_log_info)
    logger.append(file_log_warning)
    logger.append(file_log_error)

    stringer.append(file_float_to_str)
    stringer.append(file_log_datetime)
    stringer.append(file_candle_body_str)
    stringer.append(file_z_or_e_str)
    stringer.append(file_or_to_str)
    dos_arrays = DynamicOrderSettingsArrays(
        entry_size_asset=np.array([0]),
        max_equity_risk_pct=np.array([6, 9, 12]),
        max_trades=np.array([10]),
        num_candles=np.array([100]),
        risk_account_pct_size=np.array([3]),
        risk_reward=np.array([2, 4, 6]),
        sl_based_on_add_pct=np.array([0.1, 0.5, 1.0, 0.05]),
        sl_based_on_lookback=np.array([10, 30]),
        sl_bcb_type=np.array([CandleBodyType.Low]),
        sl_to_be_cb_type=np.array([CandleBodyType.Nothing]),
        sl_to_be_when_pct=np.array([0]),
        sl_to_be_ze_type=np.array([0]),
        static_leverage=np.array([0]),
        trail_sl_bcb_type=np.array([CandleBodyType.Low]),
        trail_sl_by_pct=np.array([0.1, 0.5, 1.0, 2]),
        trail_sl_when_pct=np.array([0.2, 0.5, 1, 2]),
    )
    dos_cart_arrays = dos_cart_product(
        dos_arrays=dos_arrays,
    )
    dynamic_order_settings = get_dos(
        dos_cart_arrays=dos_cart_arrays,
        dos_index=0,
    )
    indicator_settings = strat_get_current_ind_settings(
        ind_set_index=0,
        logger=logger,
    )
    logger[LoggerFuncType.Info](
        "simulate.py - run_backtest() - Created Dynamic Order Settings"
        + "\nentry_size_asset= "
        + stringer[StringerFuncType.float_to_str](dynamic_order_settings.entry_size_asset)
        + "\nmax_equity_risk_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.max_equity_risk_pct * 100, 3))
        + "\nmax_trades= "
        + str(dynamic_order_settings.max_trades)
        + "\nnum_candles= "
        + str(dynamic_order_settings.num_candles)
        + "\nrisk_account_pct_size= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.risk_account_pct_size * 100, 3))
        + "\nrisk_reward= "
        + stringer[StringerFuncType.float_to_str](dynamic_order_settings.risk_reward)
        + "\nsl_based_on_add_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.sl_based_on_add_pct * 100, 3))
        + "\nsl_based_on_lookback= "
        + str(dynamic_order_settings.sl_based_on_lookback)
        + "\nsl_bcb_type= "
        + stringer[StringerFuncType.candle_body_str](dynamic_order_settings.sl_bcb_type)
        + "\nsl_to_be_cb_type= "
        + stringer[StringerFuncType.candle_body_str](dynamic_order_settings.sl_to_be_cb_type)
        + "\nsl_to_be_when_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.sl_to_be_when_pct * 100, 3))
        + "\nsl_to_be_ze_type= "
        + stringer[StringerFuncType.z_or_e_str](dynamic_order_settings.sl_to_be_ze_type)
        + "\nstatic_leverage= "
        + stringer[StringerFuncType.float_to_str](dynamic_order_settings.static_leverage)
        + "\ntrail_sl_bcb_type= "
        + stringer[StringerFuncType.candle_body_str](dynamic_order_settings.trail_sl_bcb_type)
        + "\ntrail_sl_by_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.trail_sl_by_pct * 100, 3))
        + "\ntrail_sl_when_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.trail_sl_when_pct * 100, 3))
    )

    static_os = StaticOrderSettings(
        increase_position_type=IncreasePositionType.SmalletEntrySizeAsset,
        leverage_strategy_type=LeverageStrategyType.Dynamic,
        long_or_short=LongOrShortType.Long,
        logger_bool=True,
        pg_min_max_sl_bcb=PriceGetterType.Min,
        sl_to_be_bool=False,
        z_or_e_type=ZeroOrEntryType.Nothing,
        sl_strategy_type=StopLossStrategyType.SLBasedOnCandleBody,
        tp_strategy_type=TakeProfitStrategyType.RiskReward,
        tp_fee_type=TakeProfitFeeType.Limit,
        trail_sl_bool=True,
    )

    mufex_live = LiveMufex(
        api_key=MufexTestKeys.api_key,
        secret_key=MufexTestKeys.secret_key,
        use_test_net=True,
        timeframe="1m",
        symbol="BTCUSDT",
        trading_in="USDT",
        candles_to_dl=200,
        long_or_short=LongOrShortType.Long,
    )

    email_sender = EmailSender(
        smtp_server=EmailSenderInfo.smtp_server,
        sender_email=EmailSenderInfo.sender_email,
        password=EmailSenderInfo.password,
        receiver=EmailSenderInfo.receiver,
    )

    LiveTrading(
        dynamic_order_settings=dynamic_order_settings,
        email_sender=email_sender,
        entry_order_type=OrderPlacementType.Market,
        evaluate=strat_evaluate,
        exchange=mufex_live,
        get_strategy_plot_filename=get_strategy_plot_filename,
        ind_creator=strat_live_create_ind,
        indicator_settings=indicator_settings,
        logger=logger,
        static_os=static_os,
        stringer=stringer,
        tp_order_type=OrderPlacementType.Limit,
    ).run()
