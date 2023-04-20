import pandas as pd
import numpy as np

from quantfreedom import (
    combine_evals,
    backtest_df_only,
    simulate_up_to_6_nb,
    CandleBody,
    Arrays1dTuple,
    pdFrame,
    PossibleArray,
    Array1d,
    StaticVariables,
    sim_6_base,
    boradcast_to_1d_arrays_nb,
)
from quantfreedom.levon_qf.talib_ind_levon import from_talib


class StrategyMaker:
    def __init__(self):
        self.indicators = []
        self.combined_data = None
        self.strat_results_df = None
        self.settings_results_df = None
        self.price_data = None
        self.static_vars = None

    def from_talib(
        self,
        func_name: str,
        price_data: pdFrame = None,
        indicator_data: pdFrame = None,
        all_possible_combos: bool = False,
        column_wise_combos: bool = False,
        plot_results: bool = False,
        plot_on_data: bool = False,
        **kwargs,
    ):
        indicator = from_talib(
            func_name,
            price_data,
            indicator_data,
            all_possible_combos,
            column_wise_combos,
            plot_results,
            plot_on_data,
            **kwargs,
        )
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
        self.combined_data = b
        return b

    def backtest_df(
        self,
        # entry info
        prices: pdFrame,
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
        entries = self.combined_data
        if entries is None:
            raise ValueError("fist you have to call combine data method")
        self.price_data = prices

        self.static_vars = StaticVariables(
            equity=equity,
            divide_records_array_size_by=divide_records_array_size_by,
            fee_pct=fee_pct/100,
            gains_pct_filter=gains_pct_filter/100,
            lev_mode=lev_mode,
            max_lev=max_lev,
            max_order_size_pct=max_order_size_pct/100,
            max_order_size_value=max_order_size_value,
            min_order_size_pct=min_order_size_pct/100,
            min_order_size_value=min_order_size_value,
            mmr_pct=mmr_pct/100,
            order_type=order_type,
            size_type=size_type,
            sl_to_be_then_trail=sl_to_be_then_trail,
            sl_to_be=sl_to_be,
            total_trade_filter=total_trade_filter,
            tsl_true_or_false=tsl_true_or_false,
            upside_filter=upside_filter,
        )
        self.strat_results_df, self.settings_results_df = backtest_df_only(
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
        return self.strat_results_df, self.settings_results_df

    def select_row_and_simulate(self, row_id):
        settings = self.settings_results_df.iloc[:, row_id]

        val = settings.loc["symbol"]
        if isinstance(val, str):
            price_data = self.price_data[[settings["symbol"]]]
            entry_data = self.combined_data.iloc[:, [settings["entries_col"]]]
        else:
            price_data = self.price_data[settings.loc["symbol"].values.tolist()]
            entry_data = self.combined_data.iloc[
                :, settings.loc["entries_col"].values.tolist()
            ]

        field_names = self.settings_results_df.iloc[:, row_id].index.to_list()[2:]
        field_data = pd.DataFrame(self.settings_results_df.iloc[2:, row_id])
        try:
            field_data.loc["sl_to_be_based_on"]
            for i in CandleBody._fields:
                field_data.loc["sl_to_be_based_on"].replace(
                    i, getattr(CandleBody, i), inplace=True
                )
        except:
            pass
        try:
            field_data.loc["tsl_based_on"]
            for i in CandleBody._fields:
                field_data.loc["tsl_based_on"].replace(
                    i, getattr(CandleBody, i), inplace=True
                )
        except:
            pass
        counter = 0
        empadf = []
        for field in Arrays1dTuple._fields:
            if field == field_names[counter]:
                empadf.append(
                    np.asarray(
                        field_data.loc[field_names[counter]].values, dtype=np.float_
                    )
                )
                counter += 1
            else:
                empadf.append(np.array([np.nan]))
        empadf = Arrays1dTuple(
            leverage=empadf[0],
            max_equity_risk_pct=empadf[1]/100,
            max_equity_risk_value=empadf[2],
            risk_rewards=empadf[3],
            size_pct=empadf[4]/100,
            size_value=empadf[5],
            sl_based_on_add_pct=empadf[6]/100,
            sl_based_on=empadf[7],
            sl_pcts=empadf[8]/100,
            sl_to_be_based_on=empadf[9],
            sl_to_be_trail_by_when_pct_from_avg_entry=empadf[10]/100,
            sl_to_be_when_pct_from_avg_entry=empadf[11]/100,
            sl_to_be_zero_or_entry=empadf[12],
            tp_pcts=empadf[13]/100,
            tsl_based_on=empadf[14],
            tsl_pcts_init=empadf[15]/100,
            tsl_trail_by_pct=empadf[16]/100,
            tsl_when_pct_from_avg_entry=empadf[17]/100,
        )
        entries, broadcast_arrays = boradcast_to_1d_arrays_nb(
            arrays_1d_tuple=empadf, entries=entry_data.values
        )
        return sim_6_base(
            price_data=price_data.values,
            entries=entries,
            static_variables_tuple=self.static_vars,
            broadcast_arrays=broadcast_arrays,
        )

        return price_data, entry_data, empadf
