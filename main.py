import numpy as np
from my_stuff.my_strat import MyRsiStrategy
from quantfreedom.email_sender import EmailSender
from quantfreedom.enums import (
    CandleBodyType,
    CandleProcessingType,
    IncreasePositionType,
    LeverageStrategyType,
    LongOrShortType,
    OrderPlacementType,
    OrderSettingsArrays,
    SLToBeZeroOrEntryType,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
)
from quantfreedom.exchanges.mufex_exchange.live_mufex import LiveMufex
from quantfreedom.helper_funcs import create_os_cart_product_nb, get_order_setting
from quantfreedom.live_mode import LiveTrading
from quantfreedom.order_handler.order_handler import LongOrder
from my_stuff import EmailSenderInfo, MufexKeys, MufexTestKeys


if __name__ == "__main__":
    order_settings_arrays = OrderSettingsArrays(
        long_or_short=np.array([LongOrShortType.Long]),
        increase_position_type=np.array([IncreasePositionType.SmalletEntrySizeAsset]),
        risk_account_pct_size=np.array([0]) / 100,
        max_equity_risk_pct=np.array([0]) / 100,
        stop_loss_type=np.array([StopLossStrategyType.SLBasedOnCandleBody]),
        sl_candle_body_type=np.array([CandleBodyType.Low]),
        sl_based_on_add_pct=np.array([0.01]) / 100,
        sl_based_on_lookback=np.array([50]),
        sl_to_be_based_on_candle_body_type=np.array([CandleBodyType.Low]),
        sl_to_be_zero_or_entry_type=np.array([SLToBeZeroOrEntryType.ZeroLoss]),
        sl_to_be_when_pct_from_candle_body=np.array([2.0]) / 100,
        trail_sl_based_on_candle_body_type=np.array([CandleBodyType.Nothing]),
        trail_sl_when_pct_from_candle_body=np.array([0]) / 100,
        trail_sl_by_pct=np.array([0]) / 100,
        take_profit_type=np.array([TakeProfitStrategyType.RiskReward]),
        risk_reward=np.array([4]),
        tp_fee_type=np.array([TakeProfitFeeType.Limit]),
        leverage_type=np.array([LeverageStrategyType.Dynamic]),
        static_leverage=np.array([0.0]),
        num_candles=np.array([0]),
        entry_size_asset=np.array([0.0]),
        max_trades=np.array([3]),
    )
    os_cart_arrays = create_os_cart_product_nb(
        order_settings_arrays=order_settings_arrays,
    )
    order_settings = get_order_setting(
        os_cart_arrays=os_cart_arrays,
        order_settings_index=0,
    )
    mufex = LiveMufex(
        api_key=MufexKeys.api_key,
        secret_key=MufexKeys.secret_key,
        timeframe="5m",
        symbol="BTCUSDT",
        trading_in="USDT",
        candles_to_dl=200,
        long_or_short=LongOrShortType.Long,
        use_test_net=False,
    )
    equity = mufex.get_equity_of_asset(trading_in="USDT")

    strategy = MyRsiStrategy(
        indicator_settings_index=0,
        candle_processing_mode=CandleProcessingType.LiveTrading,
        create_trades_logger=True,
        log_debug=True,
        price_range_high=[30000],
        price_range_low=[26000],
        pivot_low_lookback=[20],
        lookback_div_period=[20],
        rsi_length=[14],
        rsi_is_below=[40],
        rsi_buffer=[0.5],
    )

    order = LongOrder(
        equity=equity,
        order_settings=order_settings,
        exchange_settings=mufex.exchange_settings,
    )

    email_sender = EmailSender(
        smtp_server=EmailSenderInfo.smtp_server,
        sender_email=EmailSenderInfo.sender_email,
        password=EmailSenderInfo.password,
        receiver=EmailSenderInfo.receiver,
    )

    LiveTrading(
        exchange=mufex,
        strategy=strategy,
        order=order,
        entry_order_type=OrderPlacementType.Market,
        tp_order_type=OrderPlacementType.Limit,
        email_sender=email_sender,
    ).run()
