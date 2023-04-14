from talib import func_name

import quantfreedom
from quantfreedom._typing import pdFrame, Union, Array1d
from quantfreedom.levon_qf.eval_lev import is_below_lev


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
        b = []
        for nm in eval_names:
            curr_val = self.eval_to_data[nm]['QuantFreedom']
            if len(b) == 0:
                b = curr_val
            else:
                b = b & curr_val
        return b

    def get_data_frame(self):
        return self.data

    def is_below(self,
                 user_args: Union[list[int, float], int, float, Array1d] = None,
                 indicator_data: pdFrame = None,
                 prices: pdFrame = None,
                 cand_ohlc: str = None,
                 plot_results: bool = False, ):
        data =  is_below_lev(self.data,
                                                           user_args,
                                                           indicator_data,
                                                           prices,
                                                           cand_ohlc,
                                                           plot_results)
        self.save_values(f'is_below{self.counter}', data)
        return data


    def is_raising(self):
        data = is_below_lev(self.data,
                                   40,
                                   )
        self.save_values('is_raising', data)
        return data
