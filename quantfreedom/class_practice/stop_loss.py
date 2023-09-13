from math import floor
import numpy as np

from quantfreedom.class_practice.enums import (
    CandleBodyType,
    DecreasePosition,
    OrderSettings,
    OrderStatus,
    SLToBeZeroOrEntryType,
    StopLossType,
)


class StopLossLong:
    sl_price_getter = None
    sl_hit_checker = None
    sl_to_be_price_getter = None
    tsl_price_getter = None

    sl_based_on_lookback = None
    sl_based_on_add_pct = None
    sl_to_be_move_when_pct = None
    sl_to_be_z_or_e = None
    trail_sl_when_pct_from_candle_body = None
    trail_sl_by_pct = None

    sl_price = None
    sl_pct = None

    def __init__(
        self,
        sl_based_on_add_pct: float,
        sl_based_on_lookback: int,
        sl_candle_body_type: CandleBodyType,
        sl_to_be_based_on_candle_body_type: CandleBodyType,
        sl_to_be_when_pct_from_candle_body: float,
        sl_to_be_zero_or_entry: int,
        sl_type: int,
        trail_sl_based_on_candle_body_type: CandleBodyType,
        trail_sl_by_pct: float,
        trail_sl_when_pct_from_candle_body: float,
    ):
        # variables
        self.sl_to_be_when_pct_from_candle_body = sl_to_be_when_pct_from_candle_body
        self.sl_to_be_move_when_pct = sl_to_be_when_pct_from_candle_body
        self.trail_sl_when_pct_from_candle_body = trail_sl_when_pct_from_candle_body
        self.trail_sl_by_pct = trail_sl_by_pct
        self.sl_based_on_lookback = sl_based_on_lookback
        self.sl_based_on_add_pct = sl_based_on_add_pct

        # setting up trailing stop loss
        self.sl_hit_checker = self.check_stop_loss_hit

        # setting up stop loss calulator
        if sl_type == StopLossType.SLBasedOnCandleBody:
            if sl_candle_body_type == CandleBodyType.Open:
                self.sl_price_getter = self.__get_candle_body_price_open
            elif sl_candle_body_type == CandleBodyType.High:
                self.sl_price_getter = self.__get_candle_body_price_high
            elif sl_candle_body_type == CandleBodyType.Low:
                self.sl_price_getter = self.__get_candle_body_price_low
            elif sl_candle_body_type == CandleBodyType.Close:
                self.sl_price_getter = self.__get_candle_body_price_close
            elif sl_candle_body_type == CandleBodyType.Nothing:
                self.sl_price_getter = self.pass_function
        elif sl_type == StopLossType.SLPct:
            self.calculator = self.sl_pct_calc
        elif sl_type == StopLossType.Nothing:
            self.calculator = self.pass_function

        # setting up stop loss break even checker
        if sl_to_be_based_on_candle_body_type == CandleBodyType.Nothing:
            self.sl_to_be_price_getter = self.pass_function
        elif sl_to_be_based_on_candle_body_type == CandleBodyType.Open:
            self.sl_to_be_price_getter = self.__get_candle_body_price_open
        elif sl_to_be_based_on_candle_body_type == CandleBodyType.High:
            self.sl_to_be_price_getter = self.__get_candle_body_price_high
        elif sl_to_be_based_on_candle_body_type == CandleBodyType.Low:
            self.sl_to_be_price_getter = self.__get_candle_body_price_low
        elif sl_to_be_based_on_candle_body_type == CandleBodyType.Close:
            self.sl_to_be_price_getter = self.__get_candle_body_price_close

        # setting up stop loss be zero or entry
        if sl_to_be_zero_or_entry != SLToBeZeroOrEntryType.Nothing:
            if sl_to_be_zero_or_entry == SLToBeZeroOrEntryType.ZeroLoss:
                self.sl_to_be_z_or_e = self.__sl_to_be_zero
            elif sl_to_be_zero_or_entry == SLToBeZeroOrEntryType.AverageEntry:
                self.sl_to_be_z_or_e = self.__sl_to_be_entry

        # setting up stop loss break even checker
        if trail_sl_based_on_candle_body_type == CandleBodyType.Nothing:
            self.tsl_price_getter = self.pass_function
        elif trail_sl_based_on_candle_body_type == CandleBodyType.Open:
            self.tsl_price_getter = self.__get_candle_body_price_open
        elif trail_sl_based_on_candle_body_type == CandleBodyType.High:
            self.tsl_price_getter = self.__get_candle_body_price_high
        elif trail_sl_based_on_candle_body_type == CandleBodyType.Low:
            self.tsl_price_getter = self.__get_candle_body_price_low
        elif trail_sl_based_on_candle_body_type == CandleBodyType.Close:
            self.tsl_price_getter = self.__get_candle_body_price_close

    def __get_candle_body_price_open(self, lookback, bar_index, symbol_price_data):
        print("Long Order - Candle Body Getter - __get_candle_body_price_open")
        # column 2 is the low because it is open high low close
        return symbol_price_data[lookback : bar_index + 1, 0].min()

    def __get_candle_body_price_high(self, lookback, bar_index, symbol_price_data):
        print("Long Order - Candle Body Getter - __get_candle_body_price_high")
        # column 2 is the low because it is open high low close
        return symbol_price_data[lookback : bar_index + 1, 1].min()

    def __get_candle_body_price_low(self, lookback, bar_index, symbol_price_data):
        print("Long Order - Candle Body Getter - __get_candle_body_price_low")
        # column 2 is the low because it is open high low close
        return symbol_price_data[lookback : bar_index + 1, 2].min()

    def __get_candle_body_price_close(self, lookback, bar_index, symbol_price_data):
        print("Long Order - Candle Body Getter - __get_candle_body_price_close")
        # column 2 is the low because it is open high low close
        return symbol_price_data[lookback : bar_index + 1, 3].min()

    # main functions
    def pass_function(self, **vargs):
        pass

    def calculate_stop_loss(self, bar_index, symbol_price_data):
        print("Long Order - Calculate Stop Loss - calculate_stop_loss")
        # lb will be bar index if sl isn't based on lookback because look back will be 0
        lookback = max(int(bar_index - self.sl_based_on_lookback), 0)
        candle_body = self.sl_price_getter(
            lookback=lookback,
            bar_index=bar_index,
            symbol_price_data=symbol_price_data,
        )
        self.sl_price = float(
            floor(candle_body - (candle_body * self.sl_based_on_add_pct))
        )
        print(f"Long Order - Calculate Stop Loss - sl_price= {self.sl_price}")
        return self.sl_price

    def check_move_stop_loss_to_be(self, **vargs):
        print("Long Order - Check Move Stop Loss to BE - check_move_stop_loss_to_be")
        

    def check_move_trailing_stop_loss(self, **vargs):
        print(
            "Long Order - Check Move Trailing Stop Loss - check_move_trailing_stop_loss"
        )
        

    def check_stop_loss_hit(self, **vargs):
        print("Long Order - Stop Loss Checker - check_stop_loss_hit")
       

    # Stop loss based on
    def sl_pct_calc(self, **vargs):
        print("Long Order - Calculate Stop Loss - sl_pct_calc")

    # stop loss to break even zero or entry
    def __sl_to_be_zero(self, **vargs):
        print("Long Order - Check Move Stop Loss to BE - __sl_to_be_zero")

    def __sl_to_be_entry(self, **vargs):
        print("Long Order - Check Move Stop Loss to BE - __sl_to_be_entry")
