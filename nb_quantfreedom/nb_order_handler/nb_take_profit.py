import numpy as np
from nb_quantfreedom.nb_custom_logger import CustomLoggerClass
from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
from numba.experimental import jitclass

from nb_quantfreedom.nb_order_handler.nb_class_helpers import nb_GetPrice
from nb_quantfreedom.nb_enums import CandleBodyType, DecreasePosition, OrderStatus


class TakeProfitClass:
    def __init__(self):
        pass

    def calculate_take_profit(
        self,
        logger: CustomLoggerClass,
        average_entry: float,
        market_fee_pct: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_reward: float,
        tp_fee_pct: float,
    ):
        pass

    def check_tp_hit(
        self,
        logger: CustomLoggerClass,
        current_candle: np.array,
        tp_price: float,
    ):
        pass


@jitclass()
class TakeProfitNB(TakeProfitClass):
    def calculate_take_profit(
        self,
        logger: CustomLoggerClass,
        average_entry: float,
        market_fee_pct: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_reward: float,
        tp_fee_pct: float,
    ):
        pass

    def check_tp_hit(
        self,
        logger: CustomLoggerClass,
        current_candle: np.array,
        tp_price: float,
    ):
        pass


@jitclass
class nb_Long_RR(TakeProfitClass):
    def calculate_take_profit(
        self,
        logger: CustomLoggerClass,
        average_entry: float,
        market_fee_pct: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_reward: float,
        tp_fee_pct: float,
    ):
        profit = possible_loss * risk_reward
        logger.log_debug(
            "nb_take_profit.py - nb_Long_RR - calculate_take_profit() - profit= " + logger.float_to_str(profit)
        )
        tp_price = (
            (profit * average_entry)
            + (average_entry * position_size_usd)
            + (average_entry * market_fee_pct * position_size_usd)
        ) / (position_size_usd * (1 - tp_fee_pct))

        tp_price = nb_round_size_by_tick_step(
            user_num=tp_price,
            exchange_num=price_tick_step,
        )
        logger.log_debug(
            "nb_take_profit.py - nb_Long_RR - calculate_take_profit() - tp_price= " + logger.float_to_str(tp_price)
        )
        # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20t%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%20%5Ccdot%5Cleft(t-e%5Cright)%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20e%20%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20t%20%5Ccdot%20%20l%5Cright)%20%3D%20p

        tp_pct = round((tp_price - average_entry) / average_entry, 3)
        logger.log_debug(
            "nb_take_profit.py - nb_Long_RR - calculate_take_profit() - tp_pct= "
            + logger.float_to_str(round(tp_pct * 100, 3))
        )
        can_move_sl_to_be = True
        logger.log_debug("nb_take_profit.py - nb_Long_RR - calculate_take_profit() - can_move_sl_to_be= True")
        return (
            can_move_sl_to_be,
            tp_price,
            tp_pct,
        )


@jitclass
class nb_Long_TPHitReg(TakeProfitClass):
    def check_tp_hit(
        self,
        logger: CustomLoggerClass,
        current_candle: np.array,
        tp_price: float,
    ):
        candle_high = nb_GetPrice().nb_price_getter(
            logger=logger,
            candle_body_type=CandleBodyType.High,
            current_candle=current_candle,
        )
        logger.log_debug(
            "nb_take_profit.py - nb_Long_TPHitReg - check_tp_hit() - candle_high= " + logger.float_to_str(candle_high)
        )
        if tp_price < candle_high:
            logger.log_debug("nb_take_profit.py - nb_Long_TPHitReg - check_tp_hit() - TP Hit")
            return True
        else:
            logger.log_debug("nb_take_profit.py - nb_Long_TPHitReg - check_tp_hit() - No Tp Hit")
            return False


@jitclass
class nb_Long_TPHitProvided(TakeProfitClass):
    def check_tp_hit(
        self,
        logger: CustomLoggerClass,
        current_candle: np.array,
        tp_price: float,
    ):
        if not np.isnan(tp_price):
            logger.log_debug(
                "nb_take_profit.py - nb_Long_TPHitReg - check_tp_hit() - Tp Hit Exit Price= "
                + logger.float_to_str(tp_price)
            )
            return True
        else:
            logger.log_debug("nb_take_profit.py - nb_Long_TPHitReg - check_tp_hit() - No Tp Hit")
            return False
