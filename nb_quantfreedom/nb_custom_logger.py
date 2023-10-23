from pandas import to_datetime
from datetime import datetime
import os, logging
import numpy as np
import time
from numba import types
from numba.experimental import jitclass
from nb_quantfreedom.nb_enums import CandleBodyType, OrderStatus, ZeroOrEntryType

from nb_quantfreedom.nb_helper_funcs import nb_float_to_str

DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FORMATTER = "%(asctime)s - %(levelname)s - %(message)s"


class CustomLoggerClass:
    def __init__(self) -> None:
        pass


class FileLogs:
    def __init__(self) -> None:
        pass

    def set_loggers(self):
        logging.Formatter.converter = time.gmtime
        # creating images folder
        complete_path = os.path.join(DIR_PATH, "logs", "images")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)

        # Info logs
        complete_path = os.path.join(DIR_PATH, "logs")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)
        filename = os.path.join(complete_path, f'info_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
        self.logger = logging.getLogger("info")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.create_logging_handler(filename, FORMATTER))
        self.logger.info("nb_custom_logger.py - nb_RegularLogs - set_loggers() - Testing info log")

        complete_path = os.path.join(DIR_PATH, "logs", "trades")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)
        filename = os.path.join(complete_path, f'trades_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
        logger = logging.getLogger("trades")
        logger.setLevel(logging.INFO)
        logger.addHandler(self.create_logging_handler(filename, FORMATTER))
        logger.info("nb_custom_logger.py - nb_RegularLogs - set_loggers() - Testing trades log")

    def create_logging_handler(self, filename: str, FORMATTER: str):
        handler = None
        try:
            handler = logging.FileHandler(
                filename=filename,
                mode="w",
            )
            handler.setFormatter(logging.Formatter(fmt=FORMATTER))
        except Exception as e:
            print(f"Couldnt init logging system with file [{filename}]. Desc=[{e}]")

        return handler

    def log_debug(self, message: str):
        self.logger.debug(message)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_warning(self, message: str):
        self.logger.warning(message)

    def log_error(self, message: str):
        self.logger.error(message)

    def float_to_str(self, x):
        return str(x)

    def log_datetime(self, candles: int):
        return str(candles[CandleBodyType.Timestamp].astype("datetime64[ms]")).replace("T", " ")

    def candle_body_str(self, number: int):
        return CandleBodyType._fields[number]

    def z_or_e_str(self, number: int):
        return ZeroOrEntryType._fields[number]

    def or_to_str(self, number: int):
        return OrderStatus._fields[number]


@jitclass
class PassLogs:
    def __init__(self) -> None:
        pass

    def log_debug(self, message: str):
        pass

    def log_info(self, message: str):
        pass

    def log_warning(self, message: str):
        pass

    def log_error(self, message: str):
        pass

    def float_to_str(self, x: float):
        pass

    def log_datetime(self, timestamp: int):
        pass

    def candle_body_str(self, number: int):
        pass

    def z_or_e_str(self, number: int):
        pass

    def or_to_str(self, number: int):
        pass


@jitclass
class PrintLogs:
    def __init__(self) -> None:
        pass

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
        print("candle body str")
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
        print("candle body str")
        if number == 0:
            return "ZeroLoss"
        if number == 1:
            return "AverageEntry"
        elif number == 2:
            return "Nothing"

    def or_to_str(self, number: int):
        print("candle body str")
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
