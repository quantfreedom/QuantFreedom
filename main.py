import os, logging
import numpy as np

from datetime import datetime
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
from quantfreedom.helper_funcs import create_os_cart_product_nb, get_order_setting_tuple_from_index
from quantfreedom.live_mode import LiveTrading
from quantfreedom.order_handler.order_handler import LongOrder
from quantfreedom.strategies.strategy import Strategy
from my_stuff import EmailSenderInfo, MufexTestKeys


def create_directory_structure():
    complete_path = os.path.join(".", "logs", "entries")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    complete_path = os.path.join(".", "logs", "images")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    complete_path = os.path.join(".", "logs", "images")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)


def create_logging_handler(filename: str, formatter: str):
    handler = None
    try:
        handler = logging.FileHandler(
            filename=filename,
            mode="w",
        )
        handler.setFormatter(logging.Formatter(formatter))
    except Exception as e:
        print(f"Couldnt init logging system with file [{filename}]. Desc=[{e}]")

    return handler


def configure_entry_logging():
    print(f"Configuring entry log level [INFO]")
    entry_logger = logging.getLogger("entry_logger")
    filename = os.path.join(
        ".",
        "logs",
        "entries",
        f'entries_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log',
    )
    formatter = "%(asctime)s - %(levelname)s - %(message)s"
    entry_logger.addHandler(create_logging_handler(filename, formatter))


def configure_server_logging():
    print(f"Configuring server log level [INFO]")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = "%(asctime)s - %(levelname)s - %(message)s"
    filename = filename = os.path.join(".", "logs", f'server_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    root.addHandler(create_logging_handler(filename, formatter))


def configure_logging():
    configure_server_logging()
    configure_entry_logging()


if __name__ == "__main__":
    create_directory_structure()

    configure_logging()

    server_logger = logging.getLogger()
    server_logger.info("testing server log")

    order_settings_arrays = OrderSettingsArrays(
        increase_position_type=np.array([IncreasePositionType.RiskPctAccountEntrySize]),
        leverage_type=np.array([LeverageStrategyType.Dynamic]),
        max_equity_risk_pct=np.array([0.002]) / 100,
        long_or_short=np.array([LongOrShortType.Long]),
        risk_account_pct_size=np.array([0.001]) / 100,
        risk_reward=np.array([2.0, 3.0, 5.0]),
        sl_based_on_add_pct=np.array([0.01, 0.02, 0.03]) / 100,
        sl_based_on_lookback=np.array([50, 70]),
        sl_candle_body_type=np.array([CandleBodyType.Low]),
        sl_to_be_based_on_candle_body_type=np.array([CandleBodyType.Nothing]),
        sl_to_be_when_pct_from_candle_body=np.array([0.0]) / 100,
        sl_to_be_zero_or_entry_type=np.array([SLToBeZeroOrEntryType.Nothing]),
        static_leverage=np.array([0.0]),
        stop_loss_type=np.array([StopLossStrategyType.SLBasedOnCandleBody]),
        take_profit_type=np.array([TakeProfitStrategyType.RiskReward]),
        tp_fee_type=np.array([TakeProfitFeeType.Limit]),
        trail_sl_based_on_candle_body_type=np.array([CandleBodyType.High]),
        trail_sl_by_pct=np.array([1.0]) / 100,
        trail_sl_when_pct_from_candle_body=np.array([3.0]) / 100,
    )
    cart_order_settings = create_os_cart_product_nb(
        order_settings_arrays=order_settings_arrays,
    )
    order_settings = get_order_setting_tuple_from_index(
        order_settings_array=cart_order_settings,
        index=2,
    )

    mufex = LiveMufex(
        api_key=MufexTestKeys.api_key,
        secret_key=MufexTestKeys.secret_key,
        timeframe="1m",
        symbol="BTCUSDT",
        trading_in="USDT",
        candles_to_dl=300,
        long_or_short=LongOrShortType.Long,
        use_test_net=True,
    )
    equity = mufex.get_equity_of_asset(trading_in="USDT")

    strategy = Strategy(
        indicator_setting_index=-1,
        candle_processing_mode=CandleProcessingType.LiveTrading,
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
