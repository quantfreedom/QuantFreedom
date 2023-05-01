from quantfreedom._typing import pdFrame, Union, Array1d
from quantfreedom.evaluators.evaluators import _combine_evals, _is_below


class Indicator:
    def __init__(self, data=None, name=""):
        self.data = data
        self.name = name
        self.evaluators = []
        self.eval_to_data = {}
        self.counter = 0

    def set_data_frame(self, df):
        self.data = df

    def save_values(self, name, data):
        self.counter += 1
        self.eval_to_data[name] = data

    def get_eval_to_data(self):
        return self.eval_to_data

    def combined_data_frame(self, eval_names):
        b = None
        for nm in eval_names:
            curr_df = self.eval_to_data[nm]
            if b is None:
                b = curr_df
            else:
                b = _combine_evals(b, curr_df)
        return b

    def get_data_frame(self):
        return self.data

    def is_below(
        self,
        user_args: Union[list[int, float], int, float, Array1d] = None,
        indicator_data: pdFrame = None,
        price_data: pdFrame = None,
        candle_ohlc: str = None,
        plot_results: bool = False,
    ):
        if indicator_data is not None:
            data = _is_below(
                user_args=user_args,
                want_to_evaluate=indicator_data,
                indicator_data=self.data,
                plot_results=plot_results,
                price_data=price_data,
                candle_ohlc=candle_ohlc,
            )
        else:
            data = _is_below(
                want_to_evaluate=self.data,
                user_args=user_args,
                indicator_data=indicator_data,
                plot_results=plot_results,
                price_data=price_data,
                candle_ohlc=candle_ohlc,
            )
        self.save_values(f"is_below{self.counter}", data)
        return data
