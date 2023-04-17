from quantfreedom import combine_evals
from quantfreedom._typing import pdFrame, Array1d
from quantfreedom.levon_qf.talib_ind_levon import from_talib


class StrategyMaker:
    def __init__(self):
        self.indicators = []

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
        self.indicators.append(indicator)
        return indicator

    def print(self):
        for v in self.indicators:
            print(v.get_eval_to_data())

    def combined_data_frame(self):
        b = None
        for indicator in self.indicators:
            eval_to_data = indicator.get_eval_to_data()
            for _, v in eval_to_data.items():
                if b is None:
                    b = v
                else:
                    b = combine_evals(b, v)
        return b
