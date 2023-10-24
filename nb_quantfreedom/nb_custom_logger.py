from numba import njit, types, typed
from numba.experimental import jitclass
from datetime import datetime
import os, logging
import time
from nb_quantfreedom.nb_enums import CandleBodyType, OrderStatus, ZeroOrEntryType

from nb_quantfreedom.nb_helper_funcs import float_to_str

DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FORMATTER = "%(asctime)s - %(levelname)s - %(message)s"


"""
#################################################
#################################################
#################################################
                File Logs
                File Logs
                File Logs
#################################################
#################################################
#################################################
"""


def set_loggers():
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
    logger = logging.getLogger("info")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_logging_handler(filename, FORMATTER))
    logger.info("nb_custom_logger.py - nb_RegularLogs - set_loggers() - Testing info log")

    complete_path = os.path.join(DIR_PATH, "logs", "trades")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)
    filename = os.path.join(complete_path, f'trades_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    logger = logging.getLogger("trades")
    logger.setLevel(logging.INFO)
    logger.addHandler(create_logging_handler(filename, FORMATTER))
    logger.info("nb_custom_logger.py - nb_RegularLogs - set_loggers() - Testing trades log")


def create_logging_handler(filename: str, FORMATTER: str):
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


def file_log_debug(message: str):
    logging.getLogger("info").debug(message)


def file_log_info(message: str):
    logging.getLogger("info").info(message)


def file_log_warning(message: str):
    logging.getLogger("info").warning(message)


def file_log_error(message: str):
    logging.getLogger("info").error(message)


def file_float_to_str(number: float):
    return str(number)


def file_log_datetime(number: float):
    return str(number.astype("datetime64[ms]")).replace("T", " ")


def file_candle_body_str(number: float):
    return CandleBodyType._fields[int(number)]


def file_z_or_e_str(number: float):
    return ZeroOrEntryType._fields[int(number)]


def file_or_to_str(number: float):
    return OrderStatus._fields[int(number)]


"""
#################################################
#################################################
#################################################
                Passing Logs
                Passing Logs
                Passing Logs
#################################################
#################################################
#################################################
"""


@njit(cache=True)
def pass_log_debug(message: str):
    pass


@njit(cache=True)
def pass_log_info(message: str):
    pass


@njit(cache=True)
def pass_log_warning(message: str):
    pass


@njit(cache=True)
def pass_log_error(message: str):
    pass


@njit(cache=True)
def pass_float_to_str(number: float):
    return ""


@njit(cache=True)
def pass_log_datetime(number: float):
    return ""


@njit(cache=True)
def pass_candle_body_str(number: float):
    return ""


@njit(cache=True)
def pass_z_or_e_str(number: float):
    return ""


@njit(cache=True)
def pass_or_to_str(number: float):
    return ""


"""
#################################################
#################################################
#################################################
                Printing Logs
                Printing Logs
                Printing Logs
#################################################
#################################################
#################################################
"""


@njit(cache=True)
def print_log_debug(message: str):
    print(message)


@njit(cache=True)
def print_log_info(message: str):
    print(message)


@njit(cache=True)
def print_log_warning(message: str):
    print(message)


@njit(cache=True)
def print_log_error(message: str):
    print(message)


@njit(cache=True)
def print_float_to_str(number: float):
    return float_to_str(number)


@njit(cache=True)
def print_log_datetime(number: float):
    return str(int(number))


@njit(cache=True)
def print_candle_body_str(number: float):
    print("candle body str")
    if number == 0:
        answer = "Timestamp"
    if number == 1:
        answer = "Open"
    elif number == 2:
        answer = "Close"
    elif number == 3:
        answer = "Low"
    elif number == 4:
        answer = "Close"
    elif number == 4:
        answer = "Volume"
    elif number == 5:
        answer = "Nothing"
    return answer


@njit(cache=True)
def print_z_or_e_str(number: float):
    print("candle body str")
    if number == 0:
        answer = "ZeroLoss"
    if number == 1:
        answer = "AverageEntry"
    elif number == 2:
        answer = "Nothing"
    return answer


@njit(cache=True)
def print_or_to_str(number: float):
    print("candle body str")
    if number == 0:
        answer = "HitMaxTrades"
    if number == 1:
        answer = "EntryFilled"
    if number == 2:
        answer = "StopLossFilled"
    elif number == 3:
        answer = "TakeProfitFilled"
    elif number == 4:
        answer = "LiquidationFilled"
    elif number == 5:
        answer = "MovedSLToBE"
    elif number == 6:
        answer = "MovedTSL"
    return answer
