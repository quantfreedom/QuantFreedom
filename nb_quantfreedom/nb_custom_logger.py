from pandas import to_datetime
from datetime import datetime
import os, logging
import numpy as np
import time
from numba.experimental import jitclass
from nb_quantfreedom.nb_enums import CandleBodyType, OrderStatus, ZeroOrEntryType

from nb_quantfreedom.nb_helper_funcs import nb_float_to_str


class CustomLoggerClass:
    def __init__(self) -> None:
        pass

    def log_debug(self, message: str):
        return ""

    def log_info(self, message: str):
        return ""

    def log_warning(self, message: str):
        return ""

    def log_error(self, message: str):
        return ""

    def float_to_str(self, x: float):
        return ""

    def log_datetime(self, timestamp: float):
        return ""

    def candle_body_str(self, number: int):
        return ""

    def z_or_e_str(self, number: int):
        return ""

    def or_to_str(self, number: int):
        return ""


@jitclass()
class CustomLoggerNB(CustomLoggerClass):
    def log_debug(self, message: str):
        return ""

    def log_info(self, message: str):
        return ""

    def log_warning(self, message: str):
        return ""

    def log_error(self, message: str):
        return ""

    def float_to_str(self, x: float):
        return ""

    def log_datetime(self, timestamp: float):
        return ""

    def candle_body_str(self, number: int):
        return ""

    def z_or_e_str(self, number: int):
        return ""

    def or_to_str(self, number: int):
        return ""


@jitclass()
class nb_PrintLogs(CustomLoggerClass):
    def log_debug(self, message: str):
        print(message)

    def log_info(self, message: str):
        print(message)

    def log_warning(self, message: str):
        print(message)

    def log_error(self, message: str):
        print(message)

    def float_to_str(self, x: float):
        return nb_float_to_str(x)

    def log_datetime(self, timestamp: int):
        return str(timestamp)

    def candle_body_str(self, number: int):
        if number == 0:
            return "Timestamp"
        if number == 1:
            return "Open"
        elif number == 2:
            return "Close"
        elif number == 3:
            return "Low"
        elif number == 4:
            return "Close"
        elif number == 4:
            return "Volume"
        elif number == 5:
            return "Nothing"

    def z_or_e_str(self, number: int):
        if number == 0:
            return "ZeroLoss"
        if number == 1:
            return "AverageEntry"
        elif number == 2:
            return "Nothing"

    def or_to_str(self, number: int):
        if number == 0:
            return "HitMaxTrades"
        if number == 1:
            return "EntryFilled"
        if number == 2:
            return "StopLossFilled"
        elif number == 3:
            return "TakeProfitFilled"
        elif number == 4:
            return "LiquidationFilled"
        elif number == 5:
            return "MovedSLToBE"
        elif number == 6:
            return "MovedTSL"


class nb_RegularLogs(CustomLoggerClass):
    def set_loggers(
        self,
        log_debug: bool,
        create_trades_logger: bool,
        custom_path: str,
        formatter: str,
    ):
        logging.Formatter.converter = time.gmtime
        # creating images folder
        complete_path = os.path.join(custom_path, "logs", "images")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)

        # Info logs
        complete_path = os.path.join(custom_path, "logs")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)
        filename = os.path.join(complete_path, f'info_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
        self.logger = logging.getLogger("info")
        if log_debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.create_logging_handler(filename, formatter))
        self.logger.info("nb_custom_logger.py - nb_RegularLogs - set_loggers() - Testing info log")

        # Trades Log
        if create_trades_logger:
            complete_path = os.path.join(custom_path, "logs", "trades")
            isExist = os.path.exists(complete_path)
            if not isExist:
                os.makedirs(complete_path)
            filename = os.path.join(complete_path, f'trades_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
            logger = logging.getLogger("trades")
            logger.setLevel(logging.INFO)
            logger.addHandler(self.create_logging_handler(filename, formatter))
            logger.info("nb_custom_logger.py - nb_RegularLogs - set_loggers() - Testing trades log")

    def create_logging_handler(self, filename: str, formatter: str):
        handler = None
        try:
            handler = logging.FileHandler(
                filename=filename,
                mode="w",
            )
            handler.setFormatter(logging.Formatter(fmt=formatter))
        except Exception as e:
            print(f"Couldnt init logging system with file [{filename}]. Desc=[{e}]")

        return handler

    def log_debug(self, message: tuple):
        logging.getLogger("info").debug(message)

    def log_info(self, message: str):
        logging.getLogger("info").info(message)

    def log_warning(self, message: str):
        logging.getLogger("info").warning(message)

    def log_error(self, message: str):
        logging.getLogger("info").error(message)

    def float_to_str(self, x):
        return str(x)

    def log_datetime(self, timestamp: int):
        return str(to_datetime(timestamp, unit="ms"))

    def candle_body_str(self, number: int):
        return CandleBodyType._fields[number]

    def z_or_e_str(self, number: int):
        return ZeroOrEntryType._fields[number]

    def or_to_str(self, number: int):
        return OrderStatus._fields[number]
