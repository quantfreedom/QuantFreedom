import numpy as np
from quantfreedom.custom_logger import set_loggers

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


if __name__ == "__main__":
    logger = []

    set_loggers()
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
