from datetime import datetime, timezone
import logging
from os.path import dirname, join, abspath, exists
from os import makedirs
from time import gmtime


def set_loggers(
    disable_logger: bool,
    log_path: str = None,
):
    if disable_logger:
        logging.getLogger().disabled = True
    else:
        try:
            logging.Formatter.converter = gmtime
            log_folder_path = join(log_path, "z_logs")

            isExist = exists(log_folder_path)
            if not isExist:
                makedirs(log_folder_path)

            file_format = f'info_{datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")}.log'
            filename = join(log_folder_path, file_format)

            logger = logging.getLogger()
            logger.disabled = False
            logger.setLevel(logging.INFO)
            logger.addHandler(create_logging_handler(filename=filename))
            logger.info("Testing info log")

        except:  # this is for the aws lambda function
            logger = logging.getLogger()
            logger.disabled = False
            logger.setLevel(logging.INFO)

            log_handler = logger.handlers[0]
            log_format = "\n%(levelname)s - %(filename)s - %(funcName)s() - %(lineno)d - %(message)s"
            log_handler.setFormatter(logging.Formatter(fmt=log_format))

            pass


def create_logging_handler(filename: str):
    handler = None
    try:
        handler = logging.FileHandler(filename=filename, mode="w")
        log_format = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s() - %(lineno)d - %(message)s"
        handler.setFormatter(logging.Formatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        raise Exception(f"Couldnt create logging handler. Desc=[{e}]")

    return handler
