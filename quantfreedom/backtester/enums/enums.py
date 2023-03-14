"""
Enums
!!! warning
    ☠️:warning:THIS IS A MASSIVE MASSIVE WARNING.:warning:☠️

    Make sure you follow what the variable types are. If it says float you have to make sure you put a \
        decimal like 1. or 3., or if it says int that you make sure there are no decimals.
    
    If you do not follow exactly what the type says for you to do then numba will start crying and wont run your code.


    Then you will be sitting there for hours trying to debug what is wrong and then you will find out it is because you put
    a number as an int instead of a float

!!! danger
    All inputs requiring you to tell it what percent you want something to be should be put in like 1. for 1% or 50. for 50%.

    If you put .01 for 1% the math will calculate it as .0001.

"""

import numpy as np

from quantfreedom import _typing as tp

__all__ = [
    'AccountAndTradeState',
    'OrderEverything',
    'OrderStatusInfo',
    'OrderStatus',
    'OrderType',
    'RejectedOrderError',
    'ResultEverything',
    'LeverageMode',
    'SizeType',

    'log_dt',
    'order_dt',
    'ready_for_df',
]


class RejectedOrderError(Exception):
    """Rejected order error."""
    pass


class AccountAndTradeState(tp.NamedTuple):
    """
    This is where you create the state of your account.

    !!! tip
        To start out create an account like this<br>
        account = AccountAndTradeState(
            available_balance=100.,
            equity=100.
            )<br>
        This will create an account with 100 dollars starting equity and starting available blanace

    Attributes:
        available_balance: `Required`
            <br>Current available balance. The available balance is based on how much cash is used.
        equity: `Required`
            <br>Current Equity. The equity is based on how much you have made or lost.
        average_entry: `Default Value = 0.`
            <br>Your current average entry.
        cash_borrowed: `Default Value = 0.`
            <br>Amount of money borrowed from the exchange
        cash_used: `Default Value = 0.`
            <br>Amount of money u are using in your trade. A.K.A. if you get liquidated this is how much you will lose.
        fee: `Default Value = 0.06`
            <br>Fee amount. This is in percent %
        leverage: `Default Value = 1.`
            <br>Current leverage being used.
        liq_price: `Default Value = 0.`
            <br>Liquidation price.
        mmr: `Default Value = .5`
            <br>Maintaince Margin Rate. This is in percent %
        position: `Default Value = 0.`
            <br>The current position size.
        realized_pnl: `Default Value = 0.`
            <br>Realized PnL from your closed trade.
        order_count_id: `Default Value = 0`
            <br>The order count used when creating order records
        log_count_id: `Default Value = 0`
            <br>The log count used when creating log records
    """
    available_balance: float
    equity: float
    average_entry: float = 0.
    cash_borrowed: float = 0.
    cash_used: float = 0.
    fee: float = 0.06
    leverage: float = 1.
    liq_price: float = 0.
    mmr: float = .5
    position: float = 0.
    realized_pnl: float = 0.
    order_count_id: int = 0
    log_count_id: int = 0


class OrderEverything(tp.NamedTuple):
    """
    How you create your order and all of the information that is stored and saved when you try to process the order.

    Attributes:
        lev_mode: `Required`
            <br>Choose a leverage mode. See [lev_mode][quantfreedom.backtester.enums.enums.LeverageModeT]
        order_type: `Required`
            <br>Choose the type or order to be processed. See [order_type][quantfreedom.backtester.enums.enums.OrderTypeT]
        size_type: `Required`
            <br>Choose the size type. See [size_type][quantfreedom.backtester.enums.enums.SizeTypeT]
        allow_partial: `Default Value = True`
            <br>Allows for your order to be partial filled.
        available_balance: `Default Value = np.nan`
            <br>Current available balance. The available balance is based on how much cash is used.
        average_entry: `Default Value = np.nan`
            <br>Your current average entry.
        cash_borrowed: `Default Value = np.nan`
            <br>Amount of money borrowed from the exchange
        cash_used: `Default Value = np.nan`
            <br>Amount of money u are using in your trade. A.K.A. if you get liquidated this is how much you will lose.
        equity: `Default Value = np.nan`
            <br>Current Equity. The equity is based on how much you have made or lost.
        fee: `Default Value = 0.06`
            <br>Fee amount. This is in percent %
        fees_paid: `Default Value = np.nan`
            <br>The total fees actually paid in USD
        leverage: `Default Value = 1.`
            <br>Current leverage being used.
        liq_price: `Default Value = 0.`
            <br>Liquidation price.
        log: `Default Value = False`
            <br>IF you want to record your log records or not
        max_equity_risk: `Default Value = np.nan`
            <br>How much of your equity you want at risk in USD
        max_equity_risk_pct: `Default Value = np.nan`
            <br>What percent of your equity do you want at risk in % like 1. for 1%
        max_lev: `Default Value = 100.`
            <br>Max leverage allowed
        max_order_pct_size: `Default Value = 100.`
            <br>What is the highest amount of percent you can make your size.
        max_order_size: `Default Value = np.inf`
            <br>The biggest you can make your position size.
        min_order_pct_size: `Default Value = .01`
            <br>The smallest percent you can make your size
        min_order_size: `Default Value = 1.`
            <br>Smallest size you can open in USD
        mmr: `Default Value = .5`
            <br>Maintenance Margin Rate. Look it up on bybit or binance.
        pct_chg: `Default Value = np.nan`
            <br>The percentage change from your average entry to your exit.
        position: `Default Value = np.nan`
            <br>The current size of your position
        raise_reject: `Default Value = False`
            <br>If there should be a rejection raised.
        realized_pnl: `Default Value = np.nan`
            <br>The realized PnL of your trade that had some sort of stop. See [PnL](https://www.bybithelp.com/bybitHC_Article?language=en_US&id=000001066)
        reject_prob: `Default Value = np.nan`
            <br>Probability of rejecting this order to simulate a random rejection event.
        risk_rewards: `Default Value = np.nan`
            <br>What you want your risk to reward to be. Put 1.5 for a 1.5 to 1 risk to reward. You must set a SL to do RR
        size: `Default Value = np.nan`
            <br>The size used for this order in USD
        size_pct: `Default Value = np.nan`
            <br>The percent risk of account or the percent of the account you want to trade. 1. for 1%
        sl_pcts: `Default Value = np.nan`
            <br>The percent you want your stop loss to be from your average entry. 1. for 1%
        sl_prices: `Default Value = np.nan`
            <br>The price you want your stop loss to be at.
        slippage_pct: `Default Value = np.nan`
            <br>Slippage percent applied to all filled orders. 1. for 1%
        status: `Default Value = np.nan`
            <br>status of the order. See [OrderStatus][quantfreedom.backtester.enums.enums.OrderStatusT]
        status_info: `Default Value = np.nan`
            <br>More info on the order status. See [OrderStatusInfo][quantfreedom.backtester.enums.enums.OrderStatusInfoT]
        tp_pcts: `Default Value = np.nan`
            <br>The percent you want your take profit to be from your average entry. 1. for 1%
        tp_prices: `Default Value = np.nan`
            <br>The price you want your take profit to be at.
        tsl_pcts: `Default Value = np.nan`
            <br>The percent you want your trailing stop loss to be from your average entry. 1. for 1%
        tsl_prices: `Default Value = np.nan`
            <br>The price you want your trailing stop loss to be at.
    """
    lev_mode: tp.Array1d
    order_type: tp.Array1d
    size_type: tp.Array1d
    # end of required
    allow_partial: tp.ArrayLike = np.array([1.])
    available_balance: tp.ArrayLike = np.array([np.nan])
    average_entry: tp.ArrayLike = np.array([np.nan])
    cash_borrowed: tp.ArrayLike = np.array([np.nan])
    cash_used: tp.ArrayLike = np.array([np.nan])
    equity: tp.ArrayLike = np.array([np.nan])
    fee: tp.ArrayLike = np.array([0.06])
    fees_paid: tp.ArrayLike = np.array([np.nan])
    leverage: tp.ArrayLike = np.array([np.nan])
    liq_price: tp.ArrayLike = np.array([np.nan])
    log: tp.ArrayLike = np.array([0.])
    max_equity_risk: tp.ArrayLike = np.array([np.nan])
    max_equity_risk_pct: tp.ArrayLike = np.array([np.nan])
    max_lev: tp.ArrayLike = np.array([100.])
    max_order_pct_size: tp.ArrayLike = np.array([100.])
    max_order_size: tp.ArrayLike = np.array([np.inf])
    min_order_pct_size: tp.ArrayLike = np.array([.01])
    min_order_size: tp.ArrayLike = np.array([1.])
    mmr: tp.ArrayLike = np.array([.5])
    pct_chg: tp.ArrayLike = np.array([np.nan])
    position: tp.ArrayLike = np.array([np.nan])
    raise_reject: tp.ArrayLike = np.array([0])
    realized_pnl: tp.ArrayLike = np.array([np.nan])
    reject_prob: tp.ArrayLike = np.array([np.nan])
    risk_rewards: tp.ArrayLike = np.array([np.nan])
    size: tp.ArrayLike = np.array([np.nan])
    size_pct: tp.ArrayLike = np.array([np.nan])
    sl_pcts: tp.ArrayLike = np.array([np.nan])
    sl_prices: tp.ArrayLike = np.array([np.nan])
    slippage_pct: tp.ArrayLike = np.array([np.nan])
    status: tp.ArrayLike = np.array([np.nan])
    status_info: tp.ArrayLike = np.array([np.nan])
    tp_pcts: tp.ArrayLike = np.array([np.nan])
    tp_prices: tp.ArrayLike = np.array([np.nan])
    tsl_pcts: tp.ArrayLike = np.array([np.nan])
    tsl_prices: tp.ArrayLike = np.array([np.nan])


class ResultEverything(tp.NamedTuple):
    """
    For now this is the exact same as OrderEverything so check that out [here][quantfreedom.backtester.enums.enums.OrderEverything]
    """
    lev_mode: float
    order_type: float
    size_type: float
    price: float
    # end of required
    allow_partial: float = 1.
    available_balance: float = np.nan
    average_entry: float = np.nan
    cash_borrowed: float = np.nan
    cash_used: float = np.nan
    equity: float = np.nan
    fee: float = 0.06
    fees_paid: float = np.nan
    leverage: float = np.nan
    liq_price: float = np.nan
    log: float = 0.
    max_equity_risk: float = np.nan
    max_equity_risk_pct: float = np.nan
    max_lev: float = 100.
    max_order_pct_size: float = 100.
    max_order_size: float = np.inf
    min_order_pct_size: float = .01
    min_order_size: float = 1.
    mmr: float = .5
    pct_chg: float = np.nan
    position: float = np.nan
    raise_reject: float = 0.
    realized_pnl: float = np.nan
    reject_prob: float = np.nan
    risk_rewards: float = np.nan
    size: float = np.nan
    size_pct: float = np.nan
    sl_pcts: float = np.nan
    sl_prices: float = np.nan
    slippage_pct: float = np.nan
    status: float = np.nan
    status_info: float = np.nan
    tp_pcts: float = np.nan
    tp_prices: float = np.nan
    tsl_pcts: float = np.nan
    tsl_prices: float = np.nan

# ############# Values ############# #


class LeverageModeT(tp.NamedTuple):
    """
    Allows you to choose which type of leverage mode you want to use.

    !!! tip
        The best way to use this would be doing something like `lev_mode=LeverageMode.Isolated`.<br>
        This is basically the same thing as saying `lev_mode=0.` and would set your leverage mode to isolated.

    Attributes:
        Isolated: `0` Regular Isolated leverage.
        LeastFreeCashUsed: `1` This auto calculates the total amount of \
            leverage needed to keep your liquidation price right below your \
            stop loss so that way you can keep as much available balance as possible.
    """
    Isolated: float = 0.
    LeastFreeCashUsed: float = 1.


LeverageMode = LeverageModeT()


class OrderStatusT(tp.NamedTuple):
    """
    Tells you what the status of trying to exucute your order.

    !!! tip
        The best way to use this would be doing something like `status=OrderStatus.Filled`.<br>
        This is basically the same thing as saying `status=0.`. and would return your order status as filled

    Attributes:
        Filled: `0.` Order has been filled.
        Ignored: `1.` Order was ignored.
        Rejected: `2.` Order was rejected for some reason.

    !!! note
        See [OrderStatusInfo][quantfreedom.backtester.enums.enums.OrderStatusInfoT] for the possible reasons \
            for the rejection
    """
    Filled: float = 0.
    Ignored: float = 1.
    Rejected: float = 2.


OrderStatus = OrderStatusT()


class OrderStatusInfoT(tp.NamedTuple):
    """
    Gives you greater detail into the order status.

    !!! tip
        The best way to use this would be doing something like `status_info=OrderStatusInfo.OrderTypeError`.<br>
        This is basically the same thing as saying `status_info=17`. and would return your order status info as order type error.

    Attributes:
        HopefullyNoProblems: `0.01`
        SizeNaN: `0.`
        PriceNaN: `1.`
        ValPriceNaN: `2.`
        ValueNaN: `3.`
        ValueZeroNeg: `4.`
        SizeZero: `5.`
        NoCashShort: `6.`
        NoCashLong: `7.`
        NoOpenPosition: `8.`
        MaxSizeExceeded: `9.`
        RandomEvent: `10.`
        CantCoverfee: `11.`
        MinSizeNotReached: `12.`
        PartialFill: `13.`
        LevToSmall: `14.`
        LevToBig: `15.`
        TPSizeTooBig: `16.`
        OrderTypeError: `17.`
        SizeAmountLessThanOne: `18.`
        NewFreeCashZeroOrLower: `19.`
        MaxEquityRisk: `20.`
        NoSLorTPHit: `21.`
    """
    HopefullyNoProblems: float = 0.01
    SizeNaN: float = 0.
    PriceNaN: float = 1.
    ValPriceNaN: float = 2.
    ValueNaN: float = 3.
    ValueZeroNeg: float = 4.
    SizeZero: float = 5.
    NoCashShort: float = 6.
    NoCashLong: float = 7.
    NoOpenPosition: float = 8.
    MaxSizeExceeded: float = 9.
    RandomEvent: float = 10.
    CantCoverfee: float = 11.
    MinSizeNotReached: float = 12.
    PartialFill: float = 13.
    LevToSmall: float = 14.
    LevToBig: float = 15.
    TPSizeTooBig: float = 16.
    OrderTypeError: float = 17.
    SizeAmountLessThanOne: float = 18.
    NewFreeCashZeroOrLower: float = 19.
    MaxEquityRisk: float = 20.
    NoSLorTPHit: float = 21.


OrderStatusInfo = OrderStatusInfoT()


class OrderTypeT(tp.NamedTuple):
    """
    Define if you want to do an entry or exit trade.

    !!! tip
        A quick exmaple would be something like this `order_type=OrderType.LongTP`.

        This is the same as saying `order_type=3.` and would set your order type to a long take profit.

    Attributes:
        LongEntry: `0.` Long Entry
        LongSL: `1.` Long Stop Loss
        LongTSL: `2.` Long Trailing Stop Loss
        LongTP: `3.` Long Take Profit
        LongLiq: `4.` Long Liquidation
        ShortEntry: `5.` Short Entry
        ShortSL: `6.` Short Stop Loss
        ShortTSL: `7.` Short Trailing Stop Loss
        ShortTP: `8.` Short Take Profit
        ShortLiq: `9.` Short Liquidation
    """
    LongEntry: float = 0.
    LongSL: float = 1.
    LongTSL: float = 2.
    LongTP: float = 3.
    LongLiq: float = 4.
    ShortEntry: float = 5.
    ShortSL: float = 6.
    ShortTSL: float = 7.
    ShortTP: float = 8.
    ShortLiq: float = 9.


OrderType = OrderTypeT()


class SizeTypeT(tp.NamedTuple):
    """
    Choosing the from the selection of how you want to process the size of your trade.

    !!! tip
        A quick exmaple would be something like this `size_type=SizeType.RiskAmount`.

        This is the same as saying size_type=2.

    !!! note
        When using risk amount or percent you will have to have a stop loss set or you will get an error.

    Attributes:
        Amount: `0.` You want to just type a size like 100. for a 100 dollar trade.
        PercentOfAccount: `1.` You want to trade a percent of your account as your tarde size.
        RiskAmount: `2.` You want to risk dollar amounts of your account, like 1. for 1 dollar risk.
        RiskPercentOfAccount: `3.` You want to risk a percent of your equity, like 1. for 1% of your equity
    """
    Amount: float = 0.
    PercentOfAccount: float = 1.
    RiskAmount: float = 2.
    RiskPercentOfAccount: float = 3.


SizeType = SizeTypeT()

# ############# Records ############# #

order_dt = np.dtype([
    ('id', np.int_),
    ('order_settings', np.int_),
    ('indicator_settings', np.int_),
    ('bar', np.int_),
    ('size', np.float_),
    ('price', np.float_),
    ('fees', np.float_),
    ('order_type', np.float_),
    ('realized_pnl', np.float_),
    ('equity', np.float_),
    ('sl_pct', np.float_),
    ('rr', np.float_),
    ('max_eq_risk_pct', np.float_),
], align=True)
"""
A numpy array with specific data types that allow you to store specific information about your order result
"""

ready_for_df = np.dtype([
    ('or_set', np.int_),
    ('ind_set', np.int_),
    ('total_trades', np.float_),
    ('gain_pct', np.float_),
    ('win_rate', np.float_),
    ('to_the_upside', np.float_),
    ('total_fees', np.float_),
    ('total_pnl', np.float_),
    ('ending_eq', np.float_),
    ('sl_pct', np.float_),
    ('rr', np.float_),
    ('max_eq_risk', np.float_),
], align=True)

order_dt = np.dtype([
    ('id', np.int_),
    ('group', np.int_),
    ('col', np.int_),
    ('idx', np.int_),
    ('size', np.float_),
    ('price', np.float_),
    ('fees', np.float_),
    ('realized_pnl', np.float_),
    ('equity', np.float_),
    ('sl_pct', np.float_),
    ('rr', np.float_),
    ('max_eq_risk_pct', np.float_),
    ('side', np.float_),
], align=True)
"""
A numpy array with specific data types that allow you to store specific information about your order result
"""

log_dt = np.dtype([
    ('order_id', np.int_),
    ('id', np.int_),
    ('col', np.int_),
    ('idx', np.int_),
    ('group', np.int_),
    ('leverage', np.float_),
    ('size', np.float_),
    ('size_usd', np.float_),
    ('price', np.float_),
    ('order_type', np.float_),
    ('avg_entry', np.float_),
    ('tp_price', np.float_),
    ('sl_price', np.float_),
    ('liq_price', np.float_),
    ('fees_paid', np.float_),
    ('realized_pnl', np.float_),
    ('equity', np.float_),
], align=True)
"""
A numpy array with specific data types that allow you to store specific information about your order result.

This is different from order records as log records is ment to store a lot of information about every order, \
    where order records is just for the filled orders and the needed info for plotting and other stuff.
"""
