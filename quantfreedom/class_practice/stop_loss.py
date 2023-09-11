from math import floor

from quantfreedom.class_practice.enums import CandleBodyType, SLToBeZeroOrEntryType, StopLossType


class StopLossLong:
    sl_calculator = None
    sl_hit_checker = None
    sl_to_be_checker = None
    
    sl_to_be_move_when_pct = None
    sl_to_be_z_or_e = None

    def __init__(
        self,
        sl_type: int,
        sl_candle_body_type: int,
        sl_to_be_based_on_candle_body_type: int,
        sl_to_be_when_pct_from_candle_body: float,
        sl_to_be_zero_or_entry: int,
    ):
        # variables
        self.sl_to_be_move_when_pct = sl_to_be_when_pct_from_candle_body
        
        # setting up trailing stop loss
        self.sl_hit_checker = self.check_stop_loss_hit
        
        # setting up stop loss calulator
        if sl_type == StopLossType.SLBasedOnCandleBody:
            if sl_candle_body_type == CandleBodyType.Open:
                self.sl_calculator = self.sl_based_on_open
            elif sl_candle_body_type == CandleBodyType.High:
                self.sl_calculator = self.sl_based_on_high
            elif sl_candle_body_type == CandleBodyType.Low:
                self.sl_calculator = self.sl_based_on_low
            elif sl_candle_body_type == CandleBodyType.Close:
                self.sl_calculator = self.sl_based_on_close
            elif sl_candle_body_type == CandleBodyType.Nothing:
                self.sl_calculator = self.pass_function
        elif sl_type == StopLossType.SLPct:
            self.calculator = self.sl_pct_calc
        elif sl_type == StopLossType.Nothing:
            self.calculator = self.pass_function

        # setting up stop loss break even checker
        if sl_to_be_based_on_candle_body_type != CandleBodyType.Nothing:
            if sl_to_be_based_on_candle_body_type == CandleBodyType.Open:
                self.sl_to_be_checker = self.sl_to_be_based_on_open
            elif sl_to_be_based_on_candle_body_type == CandleBodyType.High:
                self.sl_to_be_checker = self.sl_to_be_based_on_high
            elif sl_to_be_based_on_candle_body_type == CandleBodyType.Low:
                self.sl_to_be_checker = self.sl_to_be_based_on_low
            elif sl_to_be_based_on_candle_body_type == CandleBodyType.Close:
                self.sl_to_be_checker = self.sl_to_be_based_on_close
        elif sl_to_be_based_on_candle_body_type == CandleBodyType.Nothing:
            self.sl_to_be_checker = self.pass_function
        
        # setting up stop loss be zero or entry
        if sl_to_be_zero_or_entry != SLToBeZeroOrEntryType.Nothing:
            if sl_to_be_zero_or_entry == SLToBeZeroOrEntryType.ZeroLoss:
                self.sl_to_be_z_or_e = self.__sl_to_be_zero
            elif sl_to_be_zero_or_entry == SLToBeZeroOrEntryType.AverageEntry:
                self.sl_to_be_z_or_e = self.__sl_to_be_entry
                
    # main functions
    def calculate_stop_loss(self, **vargs):
        self.sl_calculator(**vargs)
    
    def check_stop_loss_hit(self, **vargs):
        print('Long Order - Stop Loss Checker - check_stop_loss_hit')

    def check_sl_to_be(self, **vargs):
        self.sl_to_be_checker(**vargs)

    def pass_function(self, **vargs):
        pass

    # Stop loss based on
    def sl_based_on_open(self, **vargs):
        print('Long Order - Calculate Stop Loss - sl_based_on_open')

    def sl_based_on_high(self, **vargs):
        print('Long Order - Calculate Stop Loss - sl_based_on_high')

    def sl_based_on_low(self, **vargs):
        print('Long Order - Calculate Stop Loss - sl_based_on_low')

    def sl_based_on_close(self, **vargs):
        print('Long Order - Calculate Stop Loss - sl_based_on_close')

    def sl_pct_calc(self, **vargs):
        print('Long Order - Calculate Stop Loss - sl_pct_calc')
    
    # Stop loss to break even based on

    def sl_to_be_based_on_open(self, **vargs):
        print('Long Order - Stop Loss Checker - sl_to_be_based_on_open')
        print('Long Order - Stop Loss Checker - sl_to_be_move_when_pct=', self.sl_to_be_move_when_pct)
        self.sl_to_be_z_or_e()

    def sl_to_be_based_on_high(self, **vargs):
        print('Long Order - Stop Loss Checker - sl_to_be_based_on_high')
        print('Long Order - Stop Loss Checker - sl_to_be_move_when_pct=', self.sl_to_be_move_when_pct)
        self.sl_to_be_z_or_e()

    def sl_to_be_based_on_low(self, **vargs):
        print('Long Order - Stop Loss Checker - sl_to_be_based_on_low')
        print('Long Order - Stop Loss Checker - sl_to_be_move_when_pct=', self.sl_to_be_move_when_pct)
        self.sl_to_be_z_or_e()

    def sl_to_be_based_on_close(self, **vargs):
        print('Long Order - Stop Loss Checker - sl_to_be_based_on_close')
        print('Long Order - Stop Loss Checker - sl_to_be_move_when_pct=', self.sl_to_be_move_when_pct)
        self.sl_to_be_z_or_e()
    
    # stop loss to break even zero or entry
    def __sl_to_be_zero(self, **vargs):
        print('Long Order - Stop Loss Checker - __sl_to_be_zero')
    
    def __sl_to_be_entry(self, **vargs):
        print('Long Order - Stop Loss Checker - __sl_to_be_entry')
    