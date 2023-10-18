import numpy as np
from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
from numba.experimental import jitclass

from nb_quantfreedom.nb_order_handler.nb_price_getter import nb_GetPrice
from nb_quantfreedom.np_enums import CandleBodyType, DecreasePosition, OrderStatus


class nb_TakeProfit:
    def __init__(self):
        pass

    def calculate_take_profit(
        self,
        possible_loss: float,
        position_size_usd: float,
        average_entry: float,
        risk_reward: float,
        market_fee_pct: float,
        tp_fee_pct: float,
        price_tick_step: float,
    ):
        pass

    def check_tp_hit(
        self,
        current_candle: np.array,
        exit_fee_pct: float,
        tp_price: float,
        exit_price: float,
    ):
        pass


@jitclass
class nb_Long_TPRiskReward(nb_TakeProfit):
    def calculate_take_profit(
        self,
        average_entry: float,
        market_fee_pct: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_reward: float,
        tp_fee_pct: float,
    ):
        profit = possible_loss * risk_reward
        tp_price = (
            (profit * average_entry)
            + (average_entry * position_size_usd)
            + (average_entry * market_fee_pct * position_size_usd)
        ) / (position_size_usd * (1 - tp_fee_pct))

        tp_price = nb_round_size_by_tick_step(
            user_num=tp_price,
            exchange_num=price_tick_step,
        )
        # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20t%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%20%5Ccdot%5Cleft(t-e%5Cright)%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20e%20%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20t%20%5Ccdot%20%20l%5Cright)%20%3D%20p

        tp_pct = round((tp_price - average_entry) / average_entry, 4)

        return tp_price, tp_pct, OrderStatus.EntryFilled


@jitclass
class nb_Long_TPHitReg(nb_TakeProfit):
    def check_tp_hit(
        self,
        current_candle: np.array,
        exit_fee_pct: float,
        tp_price: float,
    ):
        candle_high = nb_GetPrice().nb_price_getter(
            candle_body_type=CandleBodyType.High,
            current_candle=current_candle,
        )
        if tp_price < candle_high:
            print("Take Profit Hit")
            raise DecreasePosition(
                exit_price=tp_price,
                order_status=OrderStatus.TakeProfitFilled,
                exit_fee_pct=exit_fee_pct,
            )
        else:
            print("No tp hit")


@jitclass
class nb_Long_TPHitProvided(nb_TakeProfit):
    def check_tp_hit(
        self,
        bar_index: int,
        current_candle: np.array,
        exit_fee_pct: float,
        tp_price: float,
    ):
        if not np.isnan(tp_price):
            print("Take Profit Hit")
            raise DecreasePosition(
                exit_price=tp_price,  # sending the close of the current candle for now as exit price
                order_status=OrderStatus.TakeProfitFilled,
                exit_fee_pct=exit_fee_pct,
            )
        else:
            print("tp not hit")
        pass
