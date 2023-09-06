from math import floor

from quantfreedom.poly.enums import OrderSettings, StopLossType, CandleBody


class StopLossCalculator:
    sl_based_on_calc = None
    sl_price = None
    order_settings = None

    def __init__(
        self,
        sl_type: StopLossType,
        candle_body: CandleBody,
        order_settings: OrderSettings,
    ):
        if sl_type == StopLossType.SLBasedOnCandleBody:
            if candle_body == CandleBody.Open:
                self.sl_based_on_calc = self.sl_based_on_open
            elif candle_body == CandleBody.High:
                self.sl_based_on_calc = self.sl_based_on_high
            elif candle_body == CandleBody.Low:
                self.sl_based_on_calc = self.sl_based_on_low
            elif candle_body == CandleBody.Close:
                self.sl_based_on_calc = self.sl_based_on_close
        else:
            self.calculator = self.sl_pct_calc

        self.order_settings = order_settings

    def calc_stop_loss_based_on(self, **vargs):
        return self.sl_based_on_calc(**vargs)

    def sl_based_on_open(self, **vargs):
        pass

    def sl_based_on_high(self, **vargs):
        pass

    def sl_based_on_low(self, **vargs):
        candle_low = vargs["price_data"][2].min()
        self.sl_price = floor(
            candle_low - (candle_low * self.order_settings.sl_based_on_add_pct)
        )
        print("sl price is ", self.sl_price)
        return float(self.sl_price)

    def sl_based_on_close(self, **vargs):
        pass

    def sl_pct_calc(self, **vargs):
        pass
