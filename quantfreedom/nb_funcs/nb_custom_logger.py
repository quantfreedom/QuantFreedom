from numba import njit

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
def nb_logger(
    message: str,
):
    print(message)


@njit(cache=True)
def nb_log_datetime(
    number: float,
):
    return str(int(number))


@njit(cache=True)
def nb_candle_body_str(
    number: float,
):
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
    elif number == 5:
        answer = "Volume"
    elif number == 6:
        answer = "Nothing"
    return answer


@njit(cache=True)
def nb_os_to_str(
    number: float,
):
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
def nb_logger_pass(
    message: str,
):
    pass


@njit(cache=True)
def nb_stringer_pass(
    number: float,
):
    return str()
