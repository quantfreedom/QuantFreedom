from math import floor

from quantfreedom.class_practice.enums import CandleBodyType, StopLossType


class StopLossLong:
    sl_calculator = None
    sl_hit_checker = None
    sl_to_be_checker = None

    def __init__(
        self,
        sl_type: int,
        candle_body_type: int,
        sl_to_be_based_on_candle_body: int,
    ):
        # setting up stop loss calulator
        if sl_type == StopLossType.SLBasedOnCandleBody:
            if candle_body_type == CandleBodyType.Open:
                self.sl_calculator = self.sl_based_on_open
            elif candle_body_type == CandleBodyType.High:
                self.sl_calculator = self.sl_based_on_high
            elif candle_body_type == CandleBodyType.Low:
                self.sl_calculator = self.sl_based_on_low
            elif candle_body_type == CandleBodyType.Close:
                self.sl_calculator = self.sl_based_on_close
            elif candle_body_type == CandleBodyType.Nothing:
                self.sl_calculator = self.pass_function
        elif sl_type == StopLossType.SLPct:
            self.calculator = self.sl_pct_calc
        elif sl_type == StopLossType.Nothing:
            self.calculator = self.pass_function

        # setting up stop loss be checker
        if sl_to_be_based_on_candle_body != CandleBodyType.Nothing:
            if sl_to_be_based_on_candle_body == CandleBodyType.Open:
                self.sl_to_be_checker = self.sl_to_be_based_on_open
            elif sl_to_be_based_on_candle_body == CandleBodyType.High:
                self.sl_to_be_checker = self.sl_to_be_based_on_high
            elif sl_to_be_based_on_candle_body == CandleBodyType.Low:
                self.sl_to_be_checker = self.sl_to_be_based_on_low
            elif sl_to_be_based_on_candle_body == CandleBodyType.Close:
                self.sl_to_be_checker = self.sl_to_be_based_on_close
        elif sl_to_be_based_on_candle_body == CandleBodyType.Nothing:
            self.sl_to_be_checker = self.pass_function
        
        self.sl_hit_checker = self.stop_loss_hit_checker
        
    def calc_stop_loss(self, **vargs):
        pass
    
    def stop_loss_hit_checker(self, **vargs):
        pass

    def pass_function(self, **vargs):
        pass

    def sl_based_on_open(self, **vargs):
        pass

    def sl_based_on_high(self, **vargs):
        pass

    def sl_based_on_low(self, **vargs):
        pass

    def sl_based_on_close(self, **vargs):
        pass

    def sl_pct_calc(self, **vargs):
        pass

    def sl_to_be_based_on_open(self, **vargs):
        pass

    def sl_to_be_based_on_high(self, **vargs):
        pass

    def sl_to_be_based_on_low(self, **vargs):
        pass

    def sl_to_be_based_on_close(self, **vargs):
        pass
