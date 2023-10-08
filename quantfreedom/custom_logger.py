from datetime import datetime
import os, logging


class CustomLogger:
    def __init__(
        self,
        log_debug: bool,
        disable_logging: bool,
        create_trades_logger: bool,
        custom_path: str,
        formatter: str,
    ) -> None:
        self.__set_loggers(
            log_debug=log_debug,
            disable_logging=disable_logging,
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
            handler.setFormatter(logging.Formatter(formatter))
        except Exception as e:
            print(f"Couldnt init logging system with file [{filename}]. Desc=[{e}]")

        return handler

    def __set_loggers(self, log_debug, disable_logging, formatter, custom_path, create_trades_logger):
        # Info logs
        complete_path = os.path.join(custom_path, "logs")
        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)
        filename = os.path.join(complete_path, f'info_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
        self.info_logger = logging.getLogger("info")
        if log_debug:
            self.info_logger.setLevel(logging.DEBUG)
        else:
            self.info_logger.setLevel(logging.INFO)
        self.info_logger.addHandler(self.__create_logging_handler(filename, formatter))
        self.info_logger.disabled = disable_logging
        self.info_logger.info("Testing info log")

        # Trades Log
        if create_trades_logger:
            complete_path = os.path.join(custom_path, "logs", "trades")
            isExist = os.path.exists(complete_path)
            if not isExist:
                os.makedirs(complete_path)
            filename = os.path.join(complete_path, f'trades_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.log')
            self.trade_logger = logging.getLogger("trades")
            self.trade_logger.setLevel(logging.INFO)
            self.trade_logger.addHandler(self.__create_logging_handler(filename, formatter))
            self.trade_logger.disabled = disable_logging
            self.trade_logger.info("Testing trades log")
