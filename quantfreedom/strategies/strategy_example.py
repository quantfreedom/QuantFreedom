from quantfreedom.enums import CandleProcessingType
import pandas_ta as pta
import numpy as np


class Strategy:
    def __init__(
        self,
        candle_processing_mode=CandleProcessingType.RegularBacktest,
    ) -> None:
        if candle_processing_mode == CandleProcessingType.RegularBacktest:
            pass
        pass

    def evaluate(self, price_data, bar_index):
        return np.random.randint(5) < 2

    def ind_settings_or_results(self):
        pass

    def __run_strat(self, price_data, bar_index):
        rsi_data = pta.rsi(price_data[:, 4], bar_index)
