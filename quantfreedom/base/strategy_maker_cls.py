import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

from IPython import get_ipython
from dash import Dash, dcc, html
from jupyter_dash import JupyterDash
from dash_bootstrap_templates import load_figure_template
from IPython import get_ipython

from quantfreedom.evaluators.evaluators import _combine_evals
from quantfreedom.indicators.talib_ind import from_talib

from quantfreedom._typing import pdFrame
from quantfreedom.nb.simulate import _sim_6
from quantfreedom.plotting.strat_tabs import tabs_test_me
from quantfreedom.base.base import backtest_df_only
from quantfreedom.enums.enums import (
    CandleBody,
    OrderSettingsArrays,
    StaticVariables,
)
from quantfreedom.nb.helper_funcs import (
    boradcast_to_1d_arrays_nb,
)

load_figure_template("darkly")
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
try:
    shell = str(get_ipython())
    if "ZMQInteractiveShell" in shell:
        app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
    elif shell == "TerminalInteractiveShell":
        app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
    else:
        app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
except NameError:
    app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

bg_color = "#0b0b18"

np.set_printoptions(formatter={"float_kind": "{:.2f}".format})
pd.options.display.float_format = "{:,.2f}".format

tabs_styles = {
    "height": "60px",
    "borderBottom": "2px solid #d6d6d6",
    "fontSize": "30px",
}
tab_style = {
    "padding": "5px",
    "fontWeight": "bold",
    "backgroundColor": bg_color,
    "color": "white",
}

tab_selected_style = {
    "bordertop": "4px solid",
    "borderleft": "1px solid #d6d6d6",
    "borderright": "1px solid #d6d6d6",
    "backgroundColor": "white",
    "color": "black",
    "fontWeight": "bold",
    "padding": "5px",
}


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
                    b = _combine_evals(b, v)
        self.combined_data = b
        return b

    def backtest_df(
        self,
        price_data: pdFrame,
        static_variables_tuple: StaticVariables,
        order_settings_arrays_tuple: OrderSettingsArrays,
    ) -> tuple[pdFrame, pdFrame]:
        entries = self.combined_data
        if entries is None:
            raise ValueError("You have to call combine data method first.")

        self.price_data = price_data
        self.static_vars = static_variables_tuple

        self.strat_results_df, self.settings_results_df = backtest_df_only(
            price_data=price_data,
            entries=entries,
            static_variables_tuple=static_variables_tuple,
            order_settings_arrays_tuple=order_settings_arrays_tuple,
        )
        return self.strat_results_df, self.settings_results_df

    def strategy_dashboard(self, row_id):
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
        order_settings_list = []
        for field in OrderSettingsArrays._fields:
            try:
                if field == field_names[counter]:
                    order_settings_list.append(
                        np.asarray(
                            field_data.loc[field_names[counter]].values, dtype=np.float_
                        )
                    )
                    counter += 1
                else:
                    order_settings_list.append(np.array([np.nan]))
            except:
                order_settings_list.append(np.array([np.nan]))
        order_settings_arrays = OrderSettingsArrays(
            leverage=order_settings_list[0],
            max_equity_risk_pct=order_settings_list[1] / 100,
            max_equity_risk_value=order_settings_list[2],
            risk_reward=order_settings_list[3],
            size_pct=order_settings_list[4] / 100,
            size_value=order_settings_list[5],
            sl_based_on=order_settings_list[6],
            sl_based_on_add_pct=order_settings_list[7] / 100,
            sl_based_on_lookback=order_settings_list[8],
            sl_pct=order_settings_list[9] / 100,
            sl_to_be_based_on=order_settings_list[10],
            sl_to_be_when_pct_from_avg_entry=order_settings_list[11] / 100,
            sl_to_be_zero_or_entry=order_settings_list[12],
            tp_pct=order_settings_list[13] / 100,
            trail_sl_based_on=order_settings_list[14],
            trail_sl_by_pct=order_settings_list[15] / 100,
            trail_sl_when_pct_from_avg_entry=order_settings_list[16] / 100,
        )
        entries, os_broadcast_arrays = boradcast_to_1d_arrays_nb(
            order_settings_arrays=order_settings_arrays,
            entries=entry_data.values,
        )

        order_records = _sim_6(
            price_data=price_data.values,
            entries=entries,
            static_variables_tuple=self.static_vars,
            os_broadcast_arrays=os_broadcast_arrays,
        )

        dash_tab_list = []
        if isinstance(row_id, int):
            row_id = [row_id]

        for count, temp_id in enumerate(row_id):
            settings = self.settings_results_df.iloc[:, [temp_id]]
            indicator_dict = {}
            for i in range(len(self.indicators)):
                names = self.indicators[i].data.columns.names
                entry_names = self.combined_data.iloc[
                    :, [settings.loc["entries_col", temp_id]]
                ].columns.names
                val = []
                for n in names:
                    val.append(
                        self.combined_data.iloc[
                            :, [settings.loc["entries_col", temp_id]]
                        ].columns[0][entry_names.index(n)]
                    )
                indicator_dict[f"indicator{i}"] = {
                    f"values{i}": self.indicators[i].data[[tuple(val)]],
                    f"entries{i}": self.combined_data.iloc[
                        :, [settings.loc["entries_col", temp_id]]
                    ],
                }
                candle, pnl, dtable = tabs_test_me(
                    indicator_dict=indicator_dict,
                    prices=self.price_data[
                        indicator_dict["indicator0"]["values0"].columns[0][0]
                    ],
                    order_records=order_records[order_records["order_set_id"] == count],
                    strat_num=count + 1,
                )
                dash_tab_list.append(
                    dcc.Tab(
                        label=f"Strategy {count+1}",
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[
                            html.Div(candle),
                            html.Div(pnl),
                            html.Div(dtable),
                        ],
                    )
                )
        app.layout = html.Div(
            [
                dcc.Tabs(
                    style=tabs_styles,
                    children=dash_tab_list,
                ),
            ]
        )
        return app.run_server(debug=False)
