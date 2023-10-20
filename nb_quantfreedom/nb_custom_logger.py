from datetime import datetime
import os, logging
import time
from numba.experimental import jitclass


class nb_CustomLogger:
    def __init__(self) -> None:
        pass

    def log_debug(self, message: int):
        pass

    def log_info(self, message: str):
        pass

    def log_warning(self, message: str):
        pass

    def log_error(self, message: str):
        pass


# class nb_WillLog(nb_CustomLogger):
#     def set_loggers(
#         self,
#         log_debug: bool,
#         create_trades_logger: bool,
#         custom_path: str,
#         formatter: str,
#     ):
#         logging.Formatter.converter = time.gmtime
#         # creating images folder
#         complete_path = os.path.join(custom_path, "logs", "images")
#         isExist = os.path.exists(complete_path)
#         if not isExist:
#             os.makedirs(complete_path)

#         # Info logs
#         complete_path = os.path.join(custom_path, "logs")
#         isExist = os.path.exists(complete_path)
#         if not isExist:
#             os.makedirs(complete_path)
#         filename = os.path.join(complete_path, f'info_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
#         self.logger = logging.getLogger("info")
#         if log_debug:
#             self.logger.setLevel(logging.DEBUG)
#         else:
#             self.logger.setLevel(logging.INFO)
#         self.logger.addHandler(self.create_logging_handler(filename, formatter))
#         self.logger.info("Testing info log")

#         # Trades Log
#         if create_trades_logger:
#             complete_path = os.path.join(custom_path, "logs", "trades")
#             isExist = os.path.exists(complete_path)
#             if not isExist:
#                 os.makedirs(complete_path)
#             filename = os.path.join(complete_path, f'trades_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.log')
#             logger = logging.getLogger("trades")
#             logger.setLevel(logging.INFO)
#             logger.addHandler(self.create_logging_handler(filename, formatter))
#             logger.info("Testing trades log")

#     def create_logging_handler(self, filename: str, formatter: str):
#         handler = None
#         try:
#             handler = logging.FileHandler(
#                 filename=filename,
#                 mode="w",
#             )
#             handler.setFormatter(logging.Formatter(fmt=formatter))
#         except Exception as e:
#             print(f"Couldnt init logging system with file [{filename}]. Desc=[{e}]")

#         return handler

#     def log_debug(self, message: int):
#         logging.getLogger("info").debug(message)

#     def log_info(self, message: str):
#         logging.getLogger("info").info(message)

#     def log_warning(self, message: str):
#         logging.getLogger("info").warning(message)

#     def log_error(self, message: str):
#         logging.getLogger("info").error(message)


@jitclass()
class nb_WontLog(nb_CustomLogger):
    def log_debug(self, message: int):
        return message

    def log_info(self, message: str):
        return message

    def log_warning(self, message: str):
        return message

    def log_error(self, message: str):
        return message
