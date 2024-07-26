from datetime import datetime, timezone
from logging import getLogger, Formatter, FileHandler
from os.path import join, exists
from os import makedirs
from time import gmtime


def set_loggers(
    disable_logger: bool,
    log_path: str = None,
    log_level: str = "INFO",
):
    if disable_logger:
        getLogger().disabled = True
    else:
        try:
            Formatter.converter = gmtime
            log_folder_path = join(log_path, "z_logs")

            isExist = exists(log_folder_path)
            if not isExist:
                makedirs(log_folder_path)

            file_format = f'info_{datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")}.log'
            filename = join(log_folder_path, file_format)

            logger = getLogger()
            logger.disabled = False
            logger.setLevel(log_level.upper())
            logger.addHandler(create_logging_handler(filename=filename))
            logger.info("Testing info log")

        except:  # this is for the aws lambda function
            logger = getLogger()
            logger.disabled = False
            logger.setLevel(log_level.upper())

            log_handler = logger.handlers[0]
            log_format = "\n" + "%(levelname)s - %(filename)s - %(funcName)s() - %(lineno)d - %(message)s"
            log_handler.setFormatter(
                Formatter(
                    fmt=log_format,
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )

            pass


def create_logging_handler(filename: str):
    handler = None
    try:
        handler = FileHandler(filename=filename, mode="w")
        log_format = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s() - %(lineno)d - %(message)s"
        handler.setFormatter(
            Formatter(
                fmt=log_format,
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    except Exception as e:
        raise Exception(f"Couldnt create logging handler. Desc=[{e}]")

    return handler
