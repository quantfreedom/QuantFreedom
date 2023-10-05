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
    complete_path = os.path.join(".", "logs", "images")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    complete_path = os.path.join(".", "logs", "info")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    complete_path = os.path.join(".", "logs", "warnings")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    complete_path = os.path.join(".", "logs", "debug")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    complete_path = os.path.join(".", "logs", "errors")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    complete_path = os.path.join(".", "logs", "entries")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    complete_path = os.path.join(".", "logs", "moved_sl")
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


def configure_logging():
    formatter = "%(asctime)s - %(message)s"

    root = logging.getLogger("info")
    filename = os.path.join(".", "logs", "info", f'info_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    root.setLevel(logging.INFO)
    root.addHandler(create_logging_handler(filename, formatter))

    root = logging.getLogger("warnings")
    filename = os.path.join(".", "logs", "warnings", f'warnings_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    root.setLevel(logging.INFO)
    root.addHandler(create_logging_handler(filename, formatter))

    filename = os.path.join(".", "logs", "errors", f'errors_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    root = logging.getLogger("errors")
    root.setLevel(logging.INFO)
    root.addHandler(create_logging_handler(filename, formatter))

    filename = os.path.join(".", "logs", "debug", f'debug_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    root = logging.getLogger("debug")
    root.setLevel(logging.INFO)
    root.addHandler(create_logging_handler(filename, formatter))

    logging.ENTRY = 9
    logging.addLevelName(9, "Entry")
    filename = os.path.join(".", "logs", "entries", f'entry_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    root = logging.getLogger("entry")
    root.setLevel(logging.INFO)
    root.addHandler(create_logging_handler(filename, formatter))

    logging.MOVED_SL = 11
    logging.addLevelName(11, "Moved Stop Loss")
    filename = os.path.join(".", "logs", "moved_sl", f'moved_sl_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    root = logging.getLogger("moved_sl")
    root.setLevel(logging.INFO)
    root.addHandler(create_logging_handler(filename, formatter))


if __name__ == "__main__":
    create_directory_structure()

    configure_logging()
    logging.getLogger("info").info("Testing info logs")
    logging.getLogger("warnings").warning("Testing warning logs")
    logging.getLogger("errors").error("Testing errors logs")
    logging.getLogger("debug").info("Testing debug logs")
    logging.getLogger("entry").info("Testing entry logs")
    logging.getLogger("moved_sl").info("Testing moved stop loss")

    order_settings_arrays = OrderSettingsArrays(
        increase_position_type=np.array([IncreasePositionType.RiskPctAccountEntrySize]),
        leverage_type=np.array([LeverageStrategyType.Dynamic]),
        max_equity_risk_pct=np.array([0.002]) / 100,
        long_or_short=np.array([LongOrShortType.Long]),
        risk_account_pct_size=np.array([0.001]) / 100,
        risk_reward=np.array([2.0, 3.0, 5.0]),
        sl_based_on_add_pct=np.array([0.01, 0.02, 0.03]) / 100,
        sl_based_on_lookback=np.array([300]),
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
        candles_to_dl=400,
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
