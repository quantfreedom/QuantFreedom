from quantfreedom import combine_evals, backtest_df_only
from quantfreedom._typing import pdFrame, Array1d
from quantfreedom.levon_qf.talib_ind_levon import from_talib

import numpy as np

from quantfreedom._typing import (
    pdFrame,
    PossibleArray,
)


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

    def backtest_df(
            self,
            # entry info
            prices: pdFrame,
            entries: pdFrame,
            # required account info
            equity: float,
            fee_pct: float,
            mmr_pct: float,
            # required order
            lev_mode: int,
            order_type: int,
            size_type: int,
            # Order Params
            leverage: PossibleArray = np.nan,
            max_equity_risk_pct: PossibleArray = np.nan,
            max_equity_risk_value: PossibleArray = np.nan,
            max_order_size_pct: float = 100.0,
            min_order_size_pct: float = 0.01,
            max_order_size_value: float = np.inf,
            min_order_size_value: float = 1.0,
            max_lev: float = 100.0,
            size_pct: PossibleArray = np.nan,
            size_value: PossibleArray = np.nan,
            # Stop Losses
            sl_pcts: PossibleArray = np.nan,
            sl_to_be: bool = False,
            sl_based_on: PossibleArray = np.nan,
            sl_based_on_add_pct: PossibleArray = np.nan,
            sl_to_be_based_on: PossibleArray = np.nan,
            sl_to_be_when_pct_from_avg_entry: PossibleArray = np.nan,
            sl_to_be_zero_or_entry: PossibleArray = np.nan,  # 0 for zero or 1 for entry
            sl_to_be_then_trail: bool = False,
            sl_to_be_trail_by_when_pct_from_avg_entry: PossibleArray = np.nan,
            # Trailing Stop Loss Params
            tsl_pcts_init: PossibleArray = np.nan,
            tsl_true_or_false: bool = False,
            tsl_based_on: PossibleArray = np.nan,
            tsl_trail_by_pct: PossibleArray = np.nan,
            tsl_when_pct_from_avg_entry: PossibleArray = np.nan,
            # Take Profit Params
            risk_rewards: PossibleArray = np.nan,
            tp_pcts: PossibleArray = np.nan,
            # Results Filters
            gains_pct_filter: float = -np.inf,
            total_trade_filter: int = 0,
            divide_records_array_size_by: float = 1.0,  # between 1 and 1000
            upside_filter: float = -1.0,  # between -1 and 1
    ) -> tuple[pdFrame, pdFrame]:
        return backtest_df_only(
            prices,
            entries,
            equity,
            fee_pct,
            mmr_pct,
            lev_mode,
            order_type,
            size_type,
            leverage,
            max_equity_risk_pct,
            max_equity_risk_value,
            max_order_size_pct,
            min_order_size_pct,
            max_order_size_value,
            min_order_size_value,
            max_lev,
            size_pct,
            size_value,
            # top Losses
            sl_pcts,
            sl_to_be,
            sl_based_on,
            sl_based_on_add_pct,
            sl_to_be_based_on,
            sl_to_be_when_pct_from_avg_entry,
            sl_to_be_zero_or_entry,  # 0 for zero or 1 for entry
            sl_to_be_then_trail,
            sl_to_be_trail_by_when_pct_from_avg_entry,
            # Trailing Stop Loss Params
            tsl_pcts_init,
            tsl_true_or_false,
            tsl_based_on,
            tsl_trail_by_pct,
            tsl_when_pct_from_avg_entry,
            # Take Profit Params
            risk_rewards,
            tp_pcts,
            # Results Filters
            gains_pct_filter,
            total_trade_filter,
            divide_records_array_size_by,  # between 1 and 1000
            upside_filter,
        )
