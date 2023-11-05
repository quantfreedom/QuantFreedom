import numpy as np
from logging import getLogger
from quantfreedom.helper_funcs import round_size_by_tick_step
from quantfreedom.enums import CandleBodyType, DecreasePosition, OrderStatus, TakeProfitStrategyType

logger = getLogger("info")


class LongTakeProfit:
    risk_reward: float

    def __init__(
        self,
        market_fee_pct: float,
        price_tick_step: float,
        tp_fee_pct: float,
        tp_strategy_type: TakeProfitStrategyType,
    ):
        self.market_fee_pct = market_fee_pct
        self.price_tick_step = price_tick_step
        self.tp_fee_pct = tp_fee_pct

        if tp_strategy_type == TakeProfitStrategyType.RiskReward:
            self.tp_calculator = self.long_tp_rr
            self.checker_tp_hit = self.long_c_tp_hit_regular

    def long_tp_rr(
        self,
        average_entry: float,
        position_size_usd: float,
        possible_loss: float,
    ):
        profit = possible_loss * self.risk_reward
        logger.debug(f"profit= {profit}")
        tp_price = (
            (profit * average_entry)
            + (average_entry * position_size_usd)
            + (average_entry * self.market_fee_pct * position_size_usd)
        ) / (position_size_usd * (1 - self.tp_fee_pct))

        tp_price = round_size_by_tick_step(
            user_num=tp_price,
            exchange_num=self.price_tick_step,
        )
        logger.debug(f"tp_price= {tp_price}")
        # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20t%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%20%5Ccdot%5Cleft(t-e%5Cright)%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20e%20%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20t%20%5Ccdot%20%20l%5Cright)%20%3D%20p

        tp_pct = round((tp_price - average_entry) / average_entry, 3)
        logger.debug(f"tp_pct= {round(tp_pct * 100, 3)}")
        can_move_sl_to_be = True
        logger.debug("can_move_sl_to_be= True")
        return (
            can_move_sl_to_be,
            tp_price,
            tp_pct,
        )

    def long_c_tp_hit_regular(
        self,
        current_candle: np.array,
        tp_price: float,
    ):
        candle_high = current_candle[CandleBodyType.High]
        logger.debug(f"candle_high= {candle_high}")
        if tp_price < candle_high:
            logger.debug("TP Hit")
            raise DecreasePosition(
                exit_fee_pct=self.tp_fee_pct,
                exit_price=tp_price,
                order_status=OrderStatus.TakeProfitFilled,
            )
        else:
            logger.debug("No Tp Hit")
            pass
