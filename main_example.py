import numpy as np
from quantfreedom.custom_logger import set_loggers
from quantfreedom.email_sender import EmailSender
from quantfreedom.enums import (
    CandleBodyType,
    CandleProcessingType,
    DynamicOrderSettingsArrays,
    IncreasePositionType,
    LeverageStrategyType,
    LongOrShortType,
    OrderPlacementType,
    PriceGetterType,
    StaticOrderSettings,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
    ZeroOrEntryType,
)
from quantfreedom.exchanges.mufex_exchange.live_mufex import LiveMufex
from quantfreedom.helper_funcs import dos_cart_product, get_dos, log_dynamic_order_settings
from quantfreedom.live_mode import LiveTrading
from my_stuff import EmailSenderInfo, MufexTestKeys
from quantfreedom.order_handler.order import OrderHandler
from quantfreedom.strategies.strategy import Strategy
from logging import getLogger

logger = getLogger("info")

if __name__ == "__main__":
    set_loggers()

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
    logger.debug("set live exchange")
    try:
        equity = mufex_live.get_equity_of_asset(trading_in="USDT")
        logger.debug("got equity")
    except Exception as e:
        logger.error(f"Couldn't get equtity -> {e}")
        raise Exception(f"Couldn't get equity -> {e}")

    static_os = StaticOrderSettings(
        increase_position_type=IncreasePositionType.SmalletEntrySizeAsset,
        leverage_strategy_type=LeverageStrategyType.Dynamic,
        logger_bool=True,
        long_or_short=LongOrShortType.Long,
        pg_min_max_sl_bcb=PriceGetterType.Min,
        sl_strategy_type=StopLossStrategyType.SLBasedOnCandleBody,
        sl_to_be_bool=False,
        starting_equity=equity,
        tp_fee_type=TakeProfitFeeType.Limit,
        tp_strategy_type=TakeProfitStrategyType.RiskReward,
        trail_sl_bool=True,
        z_or_e_type=ZeroOrEntryType.Nothing,
    )
    logger.debug("set static order settings")
    dos_arrays = DynamicOrderSettingsArrays(
        max_equity_risk_pct=np.array([9, 12]),
        max_trades=np.array([3]),
        num_candles=np.array([100]),
        risk_account_pct_size=np.array([3]),
        risk_reward=np.array([2, 5]),
        sl_based_on_add_pct=np.array([0.01]),
        sl_based_on_lookback=np.array([40]),
        sl_bcb_type=np.array([CandleBodyType.Low]),
        sl_to_be_cb_type=np.array([CandleBodyType.Nothing]),
        sl_to_be_when_pct=np.array([0]),
        static_leverage=np.array([0]),
        trail_sl_bcb_type=np.array([CandleBodyType.Low]),
        trail_sl_by_pct=np.array([0.5]),
        trail_sl_when_pct=np.array([1]),
    )
    logger.debug("got dos arrays")
    dos_cart_arrays = dos_cart_product(
        dos_arrays=dos_arrays,
    )
    logger.debug("got cart product of dos")
    dynamic_order_settings = get_dos(
        dos_cart_arrays=dos_cart_arrays,
        dos_index=0,
    )
    logger.debug("got dynamic order settings")
    order = OrderHandler(
        static_os=static_os,
        exchange_settings=mufex_live.exchange_settings,
    )
    logger.debug("set order handler")
    order.update_class_dos(dynamic_order_settings=dynamic_order_settings)
    order.set_order_variables(equity=equity)
    log_dynamic_order_settings(dynamic_order_settings=dynamic_order_settings)

    email_sender = EmailSender(
        smtp_server=EmailSenderInfo.smtp_server,
        sender_email=EmailSenderInfo.sender_email,
        password=EmailSenderInfo.password,
        receiver=EmailSenderInfo.receiver,
    )
    logger.debug("set email sender")

    strategy = Strategy(
        candle_processing_type=CandleProcessingType.LiveTrading,
        rsi_is_below=np.array([100]),
        rsi_period=np.array([14]),
    )
    logger.debug("set strategy")

    strategy.set_ind_settings(
        ind_set_index=0,
    )
    strategy.log_indicator_settings()

    logger.debug("running live trading")
    LiveTrading(
        email_sender=email_sender,
        entry_order_type=OrderPlacementType.Market,
        exchange=mufex_live,
        order=order,
        strategy=strategy,
        tp_order_type=OrderPlacementType.Limit,
    ).run()
