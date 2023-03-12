import numpy as np
import pandas as pd
import polars as pl
import plotly.express as px

from quantfreedom.backtester.enums.enums import *
from quantfreedom.backtester.nb.helper_funcs import *
from quantfreedom.backtester.nb.buy_funcs import *
from quantfreedom.backtester.nb.sell_funcs import *
from quantfreedom.backtester.nb.execute_funcs import cart_tester


def cart_from_signals(
    open: tp.ArrayLike,
    high: tp.ArrayLike,
    low: tp.ArrayLike,
    close: tp.ArrayLike,
    entries: tp.ArrayLike,
    order: OrderEverything,
    account_state: AccountAndTradeState,
) -> OrderEverything:
    n = 1
    for x in order:
        n *= x.size
    # out = np.empty((n, len(order)), dtype=order_everything_dt)
    out = np.empty((n, len(order)))

    for i in range(len(order)):
        m = int(n / order[i].size)
        out[:n, i] = np.repeat(order[i], m)
        n //= order[i].size

    n = order[-1].size
    for k in range(len(order)-2, -1, -1):
        n *= order[k].size
        m = int(n / order[k].size)
        for j in range(1, order[k].size):
            out[j*m:(j+1)*m, k+1:] = out[0:m, k+1:]
    out = out.T
    mydict = {}
    for i in range(out.shape[0]):
        mydict[order._fields[i]] = out[i]
    return cart_tester(
        open=open.values,
        high=high.values,
        low=low.values,
        close=close.values,
        entries=entries.values,
        og_account_state=account_state,
        # the orders with each indv array
        lev_mode=mydict['lev_mode'],
        order_type=mydict['order_type'],
        size_type=mydict['size_type'],
        allow_partial=mydict['allow_partial'],
        available_balance=mydict['available_balance'],
        average_entry=mydict['average_entry'],
        cash_borrowed=mydict['cash_borrowed'],
        cash_used=mydict['cash_used'],
        equity=mydict['equity'],
        fee=mydict['fee'],
        fees_paid=mydict['fees_paid'],
        leverage=mydict['leverage'],
        liq_price=mydict['liq_price'],
        log=mydict['log'],
        max_equity_risk=mydict['max_equity_risk'],
        max_equity_risk_pct=mydict['max_equity_risk_pct'],
        max_lev=mydict['max_lev'],
        max_order_pct_size=mydict['max_order_pct_size'],
        max_order_size=mydict['max_order_size'],
        min_order_pct_size=mydict['min_order_pct_size'],
        min_order_size=mydict['min_order_size'],
        mmr=mydict['mmr'],
        pct_chg=mydict['pct_chg'],
        position=mydict['position'],
        raise_reject=mydict['raise_reject'],
        realized_pnl=mydict['realized_pnl'],
        reject_prob=mydict['reject_prob'],
        risk_rewards=mydict['risk_rewards'],
        size=mydict['size'],
        size_pct=mydict['size_pct'],
        sl_pcts=mydict['sl_pcts'],
        sl_prices=mydict['sl_prices'],
        slippage_pct=mydict['slippage_pct'],
        status=mydict['status'],
        status_info=mydict['status_info'],
        tp_pcts=mydict['tp_pcts'],
        tp_prices=mydict['tp_prices'],
        tsl_pcts=mydict['tsl_pcts'],
        tsl_prices=mydict['tsl_prices'],
    )
    
