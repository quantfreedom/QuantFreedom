from math import floor
from old_quantfreedom.class_practice.enums import OrderType

from old_quantfreedom.poly.enums import OrderSettings, StopLossType, CandleBody


class StopLossCalculator:
    sl_calculator = None
    sl_price = None
    order_settings = None

    def __init__(
        self,
        order_type: OrderType,
        sl_type: StopLossType,
        candle_body: CandleBody,
        order_settings: OrderSettings,
    ):
        if order_type == OrderType.Long:    
            if sl_type == StopLossType.SLBasedOnCandleBody:
                if candle_body == CandleBody.Open:
                    self.sl_calculator = self.sl_based_on_open_long
                elif candle_body == CandleBody.High:
                    self.sl_calculator = self.sl_based_on_high_long
                elif candle_body == CandleBody.Low:
                    self.sl_calculator = self.sl_based_on_low_long
                elif candle_body == CandleBody.Close:
                    self.sl_calculator = self.sl_based_on_close_long
            else:
                self.calculator = self.sl_pct_calc_long

        self.order_settings = order_settings

    def calc_stop_loss(self, **vargs):
        return self.sl_calculator(**vargs)

    def __get_sl_based_on_candles(self, symbol_price_data, bar_index):
        lb = max(int(bar_index - self.order_settings.sl_based_on_lookback), 0)
        return symbol_price_data[lb : bar_index + 1, :]

    def sl_based_on_open(self, **vargs):
        pass

    def sl_based_on_high(self, **vargs):
        pass

    def sl_based_on_low(self, **vargs):
        candle_low = self.__get_sl_based_on_candles(
            vargs["symbol_price_data"], vargs["bar_index"]
        )[:, 2].min()

        self.sl_price = floor(
            candle_low - (candle_low * self.order_settings.sl_based_on_add_pct)
        )
        print("sl price is ", self.sl_price)
        return float(self.sl_price)

    def sl_based_on_close(self, **vargs):
        pass

    def sl_pct_calc(self, **vargs):
        pass
