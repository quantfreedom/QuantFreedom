from talib import func_name

import quantfreedom
from quantfreedom._typing import pdFrame, Union, Array1d
from quantfreedom.levon_qf.eval_lev import _is_below, combine_evals


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

    def combined_data_frame(self, eval_names):
        b = None
        for nm in eval_names:
            curr_df = self.eval_to_data[nm]
            if b is None:
                b = curr_df
            else:
                b = combine_evals(b, curr_df)
        return b

    def get_data_frame(self):
        return self.data

    def is_below(
        self,
        user_args: Union[list[int, float], int, float, Array1d] = None,
        indicator_data: pdFrame = None,
        prices: pdFrame = None,
        cand_ohlc: str = None,
        plot_results: bool = False,
    ):
        if indicator_data is not None:
            data = _is_below(
                want_to_evaluate=indicator_data,
                indicator_data=self.data,
                plot_results=plot_results,
            )
        elif user_args is not None:
            data = _is_below(
                want_to_evaluate=self.data,
                user_args=user_args,
                plot_results=plot_results,
            )
        self.save_values(f"is_below{self.counter}", data)
        return data
