import numpy as np
from logging import getLogger

from quantfreedom.helpers.helper_funcs import round_size_by_tick_step
from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    FootprintCandlesTuple,
    OrderStatus,
    StopLossStrategyType,
    TrailingSLStrategyType,
)

logger = getLogger()


class GridStopLoss:
    sl_based_on_add_pct: float
    sl_based_on_lookback: int
    sl_bcb_type: int
    sl_to_be_cb_type: int
    sl_to_be_when_pct: float
    trail_sl_bcb_type: int
    trail_sl_by_pct: float
    trail_sl_when_pct: float

    def __init__(
        self,
        long_short: str,
        market_fee_pct: float,
        pg_min_max_sl_bcb: str,
        price_tick_step: float,
        sl_strategy_type: int,
        trailing_sl_strategy_type: int,
        sl_to_be_bool: bool,
        z_or_e_type: str,
    ) -> None:
        self.market_fee_pct = market_fee_pct
        self.price_tick_step = price_tick_step

        if long_short.lower() == "long":
            self.sl_to_zero_price = self.long_sl_to_zero_price
            self.get_sl_hit = self.long_sl_hit_bool
            self.move_sl_bool = self.num_greater_than_num
            self.sl_price_calc = self.decrease_sl_price
        elif long_short.lower() == "short":
            self.sl_to_zero_price = self.short_sl_to_zero_price
            self.get_sl_hit = self.short_sl_hit_bool
            self.move_sl_bool = self.num_less_than_num
            self.sl_price_calc = self.increase_sl_price
        else:
            raise Exception("long or short are the only options for long_short")

        # stop loss calulator
        if sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
            self.sl_calculator = self.sl_based_on_candle_body
            self.checker_sl_hit = self.check_sl_hit
            if pg_min_max_sl_bcb.lower() == "min":
                self.sl_bcb_price_getter = self.min_price_getter
            elif pg_min_max_sl_bcb.lower() == "max":
                self.sl_bcb_price_getter = self.max_price_getter
            else:
                raise Exception("min or max are the only options for pg_min_max_sl_bcb")
        else:
            self.sl_calculator = self.pass_func
            self.checker_sl_hit = self.pass_func

        # SL break even
        if sl_to_be_bool:
            self.checker_sl_to_be = self.check_move_sl_to_be
            # setting up stop loss be zero or entry
            if z_or_e_type.lower() == "zero":
                self.zero_or_entry_calc = self.sl_to_zero
            elif z_or_e_type.lower() == "entry":
                self.zero_or_entry_calc = self.sl_to_entry
            else:
                raise Exception("zero or entry are the only options for z_or_e_type")
        else:
            self.checker_sl_to_be = self.pass_func
            self.zero_or_entry_calc = self.pass_func

        # Trailing stop loss
        if trailing_sl_strategy_type == TrailingSLStrategyType.CBAboveBelow:
            self.checker_tsl = self.check_move_tsl_close
        elif trailing_sl_strategy_type == TrailingSLStrategyType.PctAboveBelow:
            self.checker_tsl = self.check_move_tsl_pct
            if long_short.lower() == "long":
                self.tsl_mover = self.increase_sl_price
            else:
                pass

        else:
            self.checker_tsl = self.pass_func

    def decrease_sl_price(
        self,
        price: float,
        add_pct: float,
    ):
        sl_price = price - (price * add_pct)
        return sl_price

    def increase_sl_price(
        self,
        price: float,
        add_pct: float,
    ):
        sl_price = price + (price * add_pct)
        return sl_price

    # Long Functions

    def short_sl_to_zero_price(
        self,
        average_entry: float,
    ):
        numerator = average_entry - self.market_fee_pct * average_entry
        denominator = 1 + self.market_fee_pct
        sl_price = numerator / denominator
        return sl_price

    def num_less_than_num(
        self,
        num_1: float,
        num_2: float,
    ):
        return num_1 < num_2

    # Main Functions
    def sl_to_zero(
        self,
        average_entry: float,
    ):
        sl_price = self.sl_to_zero_price(
            average_entry=average_entry,
        )
        sl_price = round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=self.price_tick_step,
        )
        return sl_price

    def sl_to_entry(
        self,
        average_entry: float,
    ):
        sl_price = average_entry
        return sl_price

    def sl_based_on_candle_body(
        self,
        bar_index: int,
        candles: FootprintCandlesTuple,
    ) -> float:
        """
        Long Stop Loss Based on Candle Body Calculator
        """
        # lb will be bar index if sl isn't based on lookback because look back will be 0
        lookback = max(bar_index - self.sl_based_on_lookback, 0)
        logger.debug(f"lookback to index= {lookback}")

        candle_body = self.sl_bcb_price_getter(
            bar_index=bar_index,
            candles=candles,
            candle_body_type=self.sl_bcb_type,
            lookback=lookback,
        )
        logger.debug(f"candle_body= {candle_body}")

        sl_price = self.sl_price_calc(
            price=candle_body,
            add_pct=self.sl_based_on_add_pct,
        )
        sl_price = round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=self.price_tick_step,
        )
        logger.debug(f"sl_price= {sl_price}")

        return sl_price

    def checker_sl_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        pass

    def check_sl_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        if self.get_sl_hit(
            current_candle=current_candle,
            sl_price=sl_price,
        ):
            logger.debug(f"Stop loss hit sl_price= {sl_price}")
            raise DecreasePosition(
                exit_fee_pct=self.market_fee_pct,
                exit_price=sl_price,
                order_status=OrderStatus.StopLossFilled,
            )
        else:
            logger.debug("No hit on stop loss")
            pass

    def long_sl_hit_bool(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        logger.debug("Starting")
        candle_low = current_candle.low_price
        logger.debug(f"candle_low= {candle_low}")
        return sl_price > candle_low

    def long_sl_to_zero_price(self, average_entry: float):
        sl_price = (average_entry + self.market_fee_pct * average_entry) / (1 - self.market_fee_pct)
        return sl_price

    def num_greater_than_num(self, num_1: float, num_2: float):
        return num_1 > num_2

    # Short Functions

    def short_sl_hit_bool(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        logger.debug("Starting")
        candle_high = current_candle.high_price
        logger.debug(f"candle_high= {candle_high}")
        return sl_price < candle_high

    def check_move_sl_to_be(
        self,
        average_entry: float,
        can_move_sl_to_be: bool,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        """
        Checking to see if we move the stop loss to break even
        """
        if can_move_sl_to_be:
            logger.debug("Might move sl to break even")
            # Stop Loss to break even
            candle_body = current_candle[self.sl_to_be_cb_type]
            pct_from_ae = abs(candle_body - average_entry) / average_entry
            logger.debug(f"pct_from_ae= {round(pct_from_ae * 100, 2)}")
            move_sl_bool = self.move_sl_bool(num_1=pct_from_ae, num_2=self.sl_to_be_when_pct)
            if move_sl_bool:
                old_sl = sl_price
                sl_price = self.zero_or_entry_calc(average_entry=average_entry)
                sl_pct = round(abs(average_entry - sl_price) / average_entry, 2)
                logger.debug(f"Moving old_sl= {old_sl} to new sl= {sl_price} sl_pct= {round(sl_pct*100, 2)}")
                return sl_price, sl_pct
            else:
                logger.debug("not moving sl to be")
                return None, None
        else:
            logger.debug("can't move sl to be")
            return None, None

    def check_move_tsl_close(
        self,
        average_entry: float,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        """
        Checking to see if we move the trailing stop loss
        """
        candle_body = current_candle[self.trail_sl_bcb_type]
        pct_from_ae = abs(candle_body - average_entry) / average_entry
        logger.debug(f"pct_from_ae= {round(pct_from_ae * 100, 2)}")
        possible_move_tsl = self.move_sl_bool(
            num_1=pct_from_ae,
            num_2=self.trail_sl_when_pct,
        )

        if possible_move_tsl:
            logger.debug("Maybe move tsl")
            temp_sl_price = self.sl_price_calc(
                price=candle_body,
                add_pct=self.trail_sl_by_pct,
            )
            temp_sl_price = round_size_by_tick_step(
                user_num=temp_sl_price,
                exchange_num=self.price_tick_step,
            )
            logger.debug(f"temp sl= {temp_sl_price}")
            if self.move_sl_bool(num_1=temp_sl_price, num_2=sl_price):
                sl_pct = round(abs(average_entry - temp_sl_price) / average_entry, 2)
                logger.debug(f"Moving tsl new sl= {temp_sl_price} > old sl= {sl_price} sl_pct= {round(sl_pct*100, 2)}")
                return temp_sl_price, sl_pct
            else:
                logger.debug("Wont move tsl")
                return None, None
        else:
            logger.debug("Not moving tsl")
            return None, None

    def check_move_tsl_pct(
        self,
        average_entry: float,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        """
        Checking to see if we move the trailing stop loss
        """
        candle_body = current_candle[self.trail_sl_bcb_type]
        pct_from_sl = abs(candle_body - sl_price) / sl_price
        logger.debug(f"pct_from_sl = {round(pct_from_sl * 100, 2)}")

        possible_move_tsl = self.move_sl_bool(
            num_1=pct_from_sl,
            num_2=self.trail_sl_when_pct,
        )

        # TODO once possible_move_tsl is True, we don't need to check it again

        if possible_move_tsl:
            logger.debug("Move tsl")
            new_sl_price = self.tsl_mover(
                price=sl_price,
                add_pct=self.trail_sl_by_pct,
            )
            round_size_by_tick_step(
                user_num=new_sl_price,
                exchange_num=self.price_tick_step,
            )
            sl_pct = round(abs(sl_price - new_sl_price) / sl_price, 2)
            return new_sl_price, sl_pct
        else:
            logger.debug("Not moving tsl")
            return None, None

    def min_price_getter(
        self,
        bar_index: int,
        candles: FootprintCandlesTuple,
        lookback: int,
        candle_body_type: int,
    ) -> float:
        the_prices = candles[candle_body_type]
        lb_the_prices = the_prices[lookback : bar_index + 1]
        final_the_prices = lb_the_prices.min()
        return final_the_prices

    def max_price_getter(
        self,
        bar_index: int,
        candles: FootprintCandlesTuple,
        lookback: int,
        candle_body_type: int,
    ) -> float:
        the_prices = candles[candle_body_type]
        lb_the_prices = the_prices[lookback : bar_index + 1]
        final_the_prices = lb_the_prices.max()
        return final_the_prices

    def pass_func(self, **kwargs):
        return None, None

    def sl_to_zero_price(self, **kwargs):
        pass

    def checker_tsl(
        self,
        average_entry: float,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        pass

    def move_sl_bool(
        self,
        num1: float,
        num2: float,
    ):
        pass

    def sl_price_calc(
        self,
        price: float,
        add_pct: float,
    ):
        pass

    def get_sl_hit(
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        pass
