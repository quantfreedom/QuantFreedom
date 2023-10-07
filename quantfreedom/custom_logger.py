from datetime import datetime
import os, logging


class CustomLogger:
    def __init__(
        self,
        log_debug: bool,
        disable_logging: bool,
    ) -> None:
        formatter = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s() - %(message)s"
        self.__create_directory_structure()
        self.__set_info_logger(log_debug=log_debug, disable_logging=disable_logging, formatter=formatter)
        self.__set_trades_logger(log_debug=log_debug, disable_logging=disable_logging, formatter=formatter)

    def __create_directory_structure(self):
        complete_path = os.path.join(".", "logs", "info")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)

        complete_path = os.path.join(".", "logs", "trades")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)

        complete_path = os.path.join(".", "logs", "images")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)

    def __create_logging_handler(self, filename: str, formatter: str):
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

    def __set_trades_logger(self, log_debug, disable_logging, formatter):
        filename = os.path.join(".", "logs", "trades", f'trades_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
        self.trade_logger = logging.getLogger("trades")
        if log_debug:
            self.trade_logger.setLevel(logging.DEBUG)
        else:
            self.trade_logger.setLevel(logging.INFO)
        self.trade_logger.addHandler(self.__create_logging_handler(filename, formatter))
        self.trade_logger.disabled = disable_logging
        self.trade_logger.info("Testing trades log")

    def __set_info_logger(self, log_debug, disable_logging, formatter):
        filename = os.path.join(".", "logs", "info", f'info_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
        self.info_logger = logging.getLogger("info")
        if log_debug:
            self.info_logger.setLevel(logging.DEBUG)
        else:
            self.info_logger.setLevel(logging.INFO)
        self.info_logger.addHandler(self.__create_logging_handler(filename, formatter))
        self.info_logger.disabled = disable_logging
        self.info_logger.info("Testing info log")
