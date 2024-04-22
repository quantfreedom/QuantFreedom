from datetime import datetime
import os, logging
import time

FORMATTER = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s() - %(lineno)d - %(message)s"


def set_loggers(
    log_folder: str,
):
    logging.Formatter.converter = time.gmtime
    # creating images folder
    complete_path = os.path.join(log_folder, "logs", "images")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)

    # Info logs
    complete_path = os.path.join(log_folder, "logs")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)
    filename = os.path.join(complete_path, f'info_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_logging_handler(filename, FORMATTER))
    logger.info("Testing info log")

    complete_path = os.path.join(log_folder, "logs", "trades")
    isExist = os.path.exists(complete_path)
    if not isExist:
        os.makedirs(complete_path)
    filename = os.path.join(complete_path, f'trades_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
    logger = logging.getLogger("trades")
    logger.setLevel(logging.INFO)
    logger.addHandler(create_logging_handler(filename, FORMATTER))
    logger.info("Testing trades log")


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
