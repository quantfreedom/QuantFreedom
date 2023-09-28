from quantfreedom.enums import CandleProcessingType


class Strategy:
    def __init__(
        self,
        candle_processing_mode=CandleProcessingType.RegularBacktest,
    ) -> None:
        if candle_processing_mode == CandleProcessingType.RegularBacktest:
            pass
        pass

    def evaluate(self):
        # will return true or false
        pass

    def ind_settings_or_results(self):
        pass
