from datetime import datetime
import os, logging
import time


class CustomLogger:
    def __init__(
        self,
        log_debug: bool,
        disable_logging: bool,
        create_trades_logger: bool,
        custom_path: str,
        formatter: str,
    ) -> None:
        logging.Formatter.converter = time.gmtime

        if disable_logging:
            logging.getLogger("info").disabled = True
            logging.getLogger("trades").disabled = True
        else:
            self.__set_loggers(
                log_debug=log_debug,
                formatter=formatter,
                custom_path=custom_path,
                create_trades_logger=create_trades_logger,
            )

    def __create_logging_handler(self, filename: str, formatter: str):
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

    def __set_loggers(self, log_debug, formatter, custom_path, create_trades_logger):
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
        info_logger = logging.getLogger("info")
        if log_debug:
            info_logger.setLevel(logging.DEBUG)
        else:
            info_logger.setLevel(logging.INFO)
        info_logger.addHandler(self.__create_logging_handler(filename, formatter))
        info_logger.info("Testing info log")

        # Trades Log
        if create_trades_logger:
            complete_path = os.path.join(custom_path, "logs", "trades")
            isExist = os.path.exists(complete_path)
            if not isExist:
                os.makedirs(complete_path)
            filename = os.path.join(complete_path, f'trades_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
            trade_logger = logging.getLogger("trades")
            trade_logger.setLevel(logging.INFO)
            trade_logger.addHandler(self.__create_logging_handler(filename, formatter))
            trade_logger.info("Testing trades log")
