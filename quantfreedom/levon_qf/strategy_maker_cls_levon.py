from quantfreedom._typing import pdFrame, Array1d
from quantfreedom.levon_qf.talib_ind_levon import from_talib


class StrategyMaker:
    def __init__(self):
        self.indicators = {}

    def from_talib(self,
                    func_name: str,
                    price_data: pdFrame = None,
                    indicator_data: pdFrame = None,
                    all_possible_combos: bool = False,
                    column_wise_combos: bool = False,
                    plot_results: bool = False,
                    plot_on_data: bool = False,
                    **kwargs,
                    ):
        indicator = from_talib(func_name,
                               price_data,
                               indicator_data,
                               all_possible_combos,
                               column_wise_combos,
                               plot_results,
                               plot_on_data,
                               **kwargs, )
        self.indicators[func_name] = indicator
        return indicator

    def print(self):
        for k, v in self.indicators.items():
            print(k, v.get_eval_to_data())
