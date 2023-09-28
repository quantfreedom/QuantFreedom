import os
import sys
import logging

sys.dont_write_bytecode = True
os.environ["NUMBA_DISABLE_JIT"] = "1"

import old_quantfreedom as qf
import pandas as pd
from old_quantfreedom.indicators.talib_ind import *
from old_quantfreedom.evaluators.evaluators import _is_below
from old_quantfreedom.base.base import backtest_df_only
from old_quantfreedom.enums.enums import (
    CandleBody,
    LeverageMode,
    OrderType,
    SizeType,
    OrderSettingsArrays,
    StaticVariables,
)

def configure_logging():
    root = logging.getLogger()

    try:
        handler = logging.FileHandler(filename='output.log', mode='w')
    except Exception as e:
        print(f'Couldnt init logging system with file [output.log]. Desc=[{e}]')
        return False

    print(f'Configuring log level [INFO]')
    root.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def run_backtester():

    prices = pd.read_hdf(os.path.join(os.getcwd(), 'tests', 'data','prices.hd5'))

    # define the indicators
    rsi = from_talib(
        func_name='rsi',
        nickname='rsi1',
        price_data=prices,
        #input_names = ['close'],
        parameters = {'timeperiod': [15, 20, 25, 30]}
    )

    ema = from_talib(
        func_name='ema',
        nickname='ema1',
        price_data=prices,
        input_names = ['close'],
        parameters = {'timeperiod': [50, 100]}
    )

    # get the entries
    entries = _is_below(
        want_to_evaluate=ema.data,
        indicator_data=rsi.data,
        # candle_ohlc= "open",
        # user_args=[50,60],
    )

    static_vars = StaticVariables(
        equity=1000.,
        lev_mode=LeverageMode.LeastFreeCashUsed,
        order_type=OrderType.LongEntry,
        size_type=SizeType.RiskPercentOfAccount,
    )

    order_settings = OrderSettingsArrays(
        max_equity_risk_pct=6.,
        risk_reward=[2,4,5],
        size_pct=1.,
        sl_based_on=CandleBody.low,
        sl_based_on_lookback=30,
        sl_based_on_add_pct=.2,
    )

    backtest_df_only(
        price_data=prices,
        entries=entries,
        static_variables_tuple=static_vars,
        order_settings_arrays_tuple=order_settings,
    )


if __name__ == '__main__':
    configure_logging()
    run_backtester()
