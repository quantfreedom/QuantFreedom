import numpy as np
from numba import njit

from quantfreedom import _typing as tp
from quantfreedom.backtester.enums.enums import *
from quantfreedom.backtester.nb.helper_funcs import *
from quantfreedom.backtester.nb.buy_funcs import *
from quantfreedom.backtester.nb.sell_funcs import *


@njit(cache=True)
def cart_tester(
    open: tp.ArrayLike,
    high: tp.ArrayLike,
    low: tp.ArrayLike,
    close: tp.ArrayLike,
    entries: tp.ArrayLike,
    og_account_state: AccountAndTradeState,
    # required
    lev_mode: tp.ArrayLike,
    order_type: tp.ArrayLike,
    size_type: tp.ArrayLike,
    # not required
    allow_partial: tp.ArrayLike = np.array([1.]),
    available_balance: tp.ArrayLike = np.array([np.nan]),
    average_entry: tp.ArrayLike = np.array([np.nan]),
    cash_borrowed: tp.ArrayLike = np.array([np.nan]),
    cash_used: tp.ArrayLike = np.array([np.nan]),
    equity: tp.ArrayLike = np.array([np.nan]),
    fee: tp.ArrayLike = np.array([0.06]),
    fees_paid: tp.ArrayLike = np.array([np.nan]),
    leverage: tp.ArrayLike = np.array([np.nan]),
    liq_price: tp.ArrayLike = np.array([np.nan]),
    log: tp.ArrayLike = np.array([0.]),
    max_equity_risk: tp.ArrayLike = np.array([np.nan]),
    max_equity_risk_pct: tp.ArrayLike = np.array([np.nan]),
    max_lev: tp.ArrayLike = np.array([100.]),
    max_order_pct_size: tp.ArrayLike = np.array([100.]),
    max_order_size: tp.ArrayLike = np.array([np.inf]),
    min_order_pct_size: tp.ArrayLike = np.array([.01]),
    min_order_size: tp.ArrayLike = np.array([1.]),
    mmr: tp.ArrayLike = np.array([.5]),
    pct_chg: tp.ArrayLike = np.array([np.nan]),
    position: tp.ArrayLike = np.array([np.nan]),
    raise_reject: tp.ArrayLike = np.array([0.]),
    realized_pnl: tp.ArrayLike = np.array([np.nan]),
    reject_prob: tp.ArrayLike = np.array([np.nan]),
    risk_rewards: tp.ArrayLike = np.array([np.nan]),
    size: tp.ArrayLike = np.array([np.nan]),
    size_pct: tp.ArrayLike = np.array([np.nan]),
    sl_pcts: tp.ArrayLike = np.array([np.nan]),
    sl_prices: tp.ArrayLike = np.array([np.nan]),
    slippage_pct: tp.ArrayLike = np.array([np.nan]),
    status: tp.ArrayLike = np.array([np.nan]),
    status_info: tp.ArrayLike = np.array([np.nan]),
    tp_pcts: tp.ArrayLike = np.array([np.nan]),
    tp_prices: tp.ArrayLike = np.array([np.nan]),
    tsl_pcts: tp.ArrayLike = np.array([np.nan]),
    tsl_prices: tp.ArrayLike = np.array([np.nan]),
) -> tp.Tuple[tp.RecordArray, tp.RecordArray]:

    total_order_settings = sl_pcts.size
    
    if entries.ndim == 1:
        total_indicator_settings = 1
    else:
        total_indicator_settings = entries.shape[1]
        
    total_bars = open.size

    record_count = 100000
    # for i in range(total_order_settings):
    #     for ii in range(total_indicator_settings):
    #         for iii in range(total_bars):
    #             if entries[:, ii][iii]:
    #                 record_count += 1
    # record_count = int(record_count / 2)

    # need to figure out how to make this number would be easier to do it after because then i would know exactly how big to make it
    # but then that would require a for loop at the end which isn't a problem but don't want to do the math to figure it out lol
    # because numba might make it annoying

    df_array = np.empty(10000, dtype=ready_for_df)
    df_counter = 0
    order_records = np.empty(record_count, dtype=order_dt)
    order_count_id = 0

    log_records = np.empty(record_count, dtype=log_dt)
    log_count_id = 0

    start_order_count = 0
    end_order_count = 0

    start_log_count = 0
    end_log_count = 0

    for os in range(total_order_settings):
        order = order_nb(
            lev_mode=lev_mode[os],
            order_type=order_type[os],
            size_type=size_type[os],
            # not required
            allow_partial=allow_partial[os],
            available_balance=available_balance[os],
            average_entry=average_entry[os],
            cash_borrowed=cash_borrowed[os],
            cash_used=cash_used[os],
            equity=equity[os],
            fee=fee[os],
            fees_paid=fees_paid[os],
            leverage=leverage[os],
            liq_price=liq_price[os],
            log=log[os],
            max_equity_risk=max_equity_risk[os],
            max_equity_risk_pct=max_equity_risk_pct[os],
            max_lev=max_lev[os],
            max_order_pct_size=max_order_pct_size[os],
            max_order_size=max_order_size[os],
            min_order_pct_size=min_order_pct_size[os],
            min_order_size=min_order_size[os],
            mmr=mmr[os],
            pct_chg=pct_chg[os],
            position=position[os],
            raise_reject=raise_reject[os],
            realized_pnl=realized_pnl[os],
            reject_prob=reject_prob[os],
            risk_rewards=risk_rewards[os],
            size=size[os],
            size_pct=size_pct[os],
            sl_pcts=sl_pcts[os],
            sl_prices=sl_prices[os],
            slippage_pct=slippage_pct[os],
            status=status[os],
            status_info=status_info[os],
            tp_pcts=tp_pcts[os],
            tp_prices=tp_prices[os],
            tsl_pcts=tsl_pcts[os],
            tsl_prices=tsl_prices[os],
        )

        for indicator_settings in range(total_indicator_settings):

            if entries.ndim != 1:
                current_indicator_entries = entries[:,
                                                    indicator_settings]
            else:
                current_indicator_entries = entries
                
            temp_order_records = np.empty(total_bars, dtype=order_dt)
            temp_log_records = np.empty(total_bars, dtype=log_dt)
            n = 0

            account_state = AccountAndTradeState(
                available_balance=og_account_state.available_balance,
                equity=og_account_state.equity,
                average_entry=og_account_state.average_entry,
                cash_borrowed=og_account_state.cash_borrowed,
                cash_used=og_account_state.cash_used,
                fee=og_account_state.fee,
                leverage=og_account_state.leverage,
                liq_price=og_account_state.liq_price,
                mmr=og_account_state.mmr,
                position=og_account_state.position,
                realized_pnl=og_account_state.realized_pnl,
                order_count_id=order_count_id,
                log_count_id=log_count_id,
            )
            for bar in range(total_bars):

                if account_state.available_balance < 1:
                    break

                if current_indicator_entries[bar]:
                    account_state, order_result = process_order_nb(
                        bar=bar,
                        col=indicator_settings,
                        price=open[bar],
                        group=os,
                        account_state=account_state,
                        order=order,
                        order_records=temp_order_records[n],
                        log_records=None,
                    )
                    if order_result.status == 0.:
                        n += 1
                        order_count_id += 1
                        log_count_id += 1
                if account_state.position > 0:
                    order_tp_sl, price_tp_sl = check_sl_tp_nb(
                        high[bar],
                        low[bar],
                        order_result
                    )
                    if not np.isnan(order_tp_sl.size):
                        account_state, stop_order_result = process_order_nb(
                            bar=bar,
                            col=indicator_settings,
                            group=os,
                            price=price_tp_sl,
                            account_state=account_state,
                            order=order_tp_sl,
                            order_records=temp_order_records[n],
                            log_records=None,
                        )
                        if stop_order_result.status == 0.:
                            n += 1
                            order_count_id += 1
                            log_count_id += 1
            gains_pct = ((account_state.equity - og_account_state.equity) / og_account_state.equity) * 100       
            if gains_pct > 50:
                temp_order_records = temp_order_records[:n]
                w_l = temp_order_records['realized_pnl'][~np.isnan(
                    temp_order_records['realized_pnl'])]
                if w_l.size > 30:  # this is more than 30 trades
                    end_order_count += n
                    order_records[start_order_count: end_order_count] = temp_order_records
                    start_order_count = end_order_count

                    # win rate calc
                    win_loss = np.where(w_l < 0, 0, 1)
                    win_rate = round(np.count_nonzero(
                        win_loss) / win_loss.size * 100, 2)

                    total_pnl = temp_order_records['realized_pnl'][~np.isnan(
                        temp_order_records['realized_pnl'])].sum()

                    gain_pct = (
                        temp_order_records['equity'][n-1] - temp_order_records['equity'][0]) / temp_order_records['equity'][0] * 100

                    # to_the_upside calculation
                    x = np.arange(1, len(w_l)+1)
                    y = w_l.cumsum()

                    xm = x.mean()
                    ym = y.mean()

                    y_ym = y - ym
                    y_ym_s = y_ym**2

                    x_xm = x - xm
                    x_xm_s = x_xm**2

                    b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
                    b0 = ym - b1 * xm

                    y_pred = b0 + b1 * x

                    yp_ym = y_pred - ym

                    yp_ym_s = yp_ym**2
                    to_the_upside = yp_ym_s.sum() / y_ym_s.sum()

                    df_array['or_set'][df_counter] = temp_order_records['group'][0]
                    df_array['ind_set'][df_counter] = temp_order_records['col'][0]
                    df_array['total_trades'][df_counter] = w_l.size
                    df_array['gain_pct'][df_counter] = gain_pct
                    df_array['win_rate'][df_counter] = win_rate
                    df_array['to_the_upside'][df_counter] = to_the_upside
                    df_array['total_fees'][df_counter] = temp_order_records['fees'].sum()
                    df_array['total_pnl'][df_counter] = total_pnl
                    df_array['ending_eq'][df_counter] = temp_order_records['equity'][-1]
                    df_array['sl_pct'][df_counter] = temp_order_records['sl_pct'][0]
                    df_array['rr'][df_counter] = temp_order_records['rr'][0]
                    df_array['max_eq_risk'][df_counter] = temp_order_records['max_eq_risk_pct'][0]
                    df_counter += 1

            # TODO make it so log records works
            # if order.log == 1.:
            #     end_log_count += n
            #     log_records[start_log_count : end_log_count] = temp_log_records[ : n]
            #     start_log_count = end_log_count

    return df_array[:df_counter], order_records[: end_order_count], log_records[: 50]


@njit(cache=True)
def check_sl_tp_nb(
    high: float,
    low: float,
    order_result: ResultEverything,
) -> OrderEverything:
    """
    This checks if your stop or take profit was hit.

    Args:
        high: The high of the candle
        low: The low of the candle
        order_result: See [Order Result][quantfreedom.backtester.enums.enums.ResultEverything].

    !!! note
        Right now it only fully closes the position. But that will be changing soon once multiple stops is implimented.

    First it checks the order type and then it checks if the stop losses were hit and then checks to see if take profit was hit last.
    It defaults to checking tp last so it has a negative bias.
    """
    size = np.inf
    # checking if we are in a long
    if order_result.order_type == OrderType.LongEntry:
        # Regular Stop Loss
        if low <= order_result.sl_prices:
            price = order_result.sl_prices
            order_type = OrderType.LongSL
        # Trailing Stop Loss
        elif low <= order_result.tsl_prices:
            price = order_result.tsl_prices
            order_type = OrderType.LongTSL
        # Liquidation
        elif low <= order_result.liq_price:
            price = order_result.liq_price
            order_type = OrderType.LongLiq
        # Take Profit
        elif high >= order_result.tp_prices:
            price = order_result.tp_prices
            order_type = OrderType.LongTP
        else:
            order_type = OrderType.LongEntry
            price = np.nan
            size = np.nan

    # Checking if we are a short entry
    elif order_result.order_type == OrderType.ShortEntry:
        # Stop Loss
        if high >= order_result.sl_prices:
            price = order_result.sl_prices
            order_type = OrderType.ShortSL
        # Trailing Stop Loss
        elif high >= order_result.tsl_prices:
            price = order_result.tsl_prices
            order_type = OrderType.ShortTSL
        # Liquidation
        elif high >= order_result.liq_price:
            price = order_result.liq_price
            order_type = OrderType.ShortLiq
        # Take Profit
        elif low <= order_result.tp_prices:
            price = order_result.tp_prices
            order_type = OrderType.ShortTP
        else:
            order_type = OrderType.ShortEntry
            price = np.nan
            size = np.nan
    else:
        raise RejectedOrderError(
            "Check SL TP: Something is wrong checking sl tsl tp")
    # create the order
    new_order = order_nb(
        # required
        lev_mode=order_result.lev_mode,
        order_type=order_type,
        size_type=SizeType.Amount,
        # not required
        allow_partial=order_result.allow_partial,
        available_balance=order_result.available_balance,
        average_entry=order_result.average_entry,
        cash_borrowed=order_result.cash_borrowed,
        cash_used=order_result.cash_used,
        equity=order_result.equity,
        fee=order_result.fee,
        fees_paid=order_result.fees_paid,
        leverage=order_result.leverage,
        liq_price=order_result.liq_price,
        log=order_result.log,
        max_equity_risk=order_result.max_equity_risk,
        max_equity_risk_pct=order_result.max_equity_risk_pct,
        max_lev=order_result.max_lev,
        max_order_pct_size=order_result.max_order_pct_size,
        max_order_size=order_result.max_order_size,
        min_order_pct_size=order_result.min_order_pct_size,
        min_order_size=order_result.min_order_size,
        mmr=order_result.mmr,
        pct_chg=order_result.pct_chg,
        position=order_result.position,
        raise_reject=order_result.raise_reject,
        realized_pnl=order_result.realized_pnl,
        reject_prob=order_result.reject_prob,
        risk_rewards=np.nan,
        size=size,
        size_pct=np.nan,
        sl_pcts=np.nan,
        sl_prices=order_result.sl_prices,
        slippage_pct=order_result.slippage_pct,
        status=OrderStatus.Filled,
        status_info=OrderStatusInfo.HopefullyNoProblems,
        tp_pcts=np.nan,
        tp_prices=order_result.tp_prices,
        tsl_pcts=np.nan,
        tsl_prices=order_result.tsl_prices,
    )
    return new_order, price


@njit(cache=True)
def order_nb(
    # required
    lev_mode,
    order_type,
    size_type,
    # not required
    allow_partial=np.array([1.]),
    available_balance=np.array([np.nan]),
    average_entry=np.array([np.nan]),
    cash_borrowed=np.array([np.nan]),
    cash_used=np.array([np.nan]),
    equity=np.array([np.nan]),
    fee=np.array([0.06]),
    fees_paid=np.array([np.nan]),
    leverage=np.array([np.nan]),
    liq_price=np.array([np.nan]),
    log=np.array([0.]),
    max_equity_risk=np.array([np.nan]),
    max_equity_risk_pct=np.array([np.nan]),
    max_lev=np.array([100.]),
    max_order_pct_size=np.array([100.]),
    max_order_size=np.array([np.inf]),
    min_order_pct_size=np.array([.01]),
    min_order_size=np.array([1.]),
    mmr=np.array([.5]),
    pct_chg=np.array([np.nan]),
    position=np.array([np.nan]),
    raise_reject=np.array([0.]),
    realized_pnl=np.array([np.nan]),
    reject_prob=np.array([np.nan]),
    risk_rewards=np.array([np.nan]),
    size=np.array([np.nan]),
    size_pct=np.array([np.nan]),
    sl_pcts=np.array([np.nan]),
    sl_prices=np.array([np.nan]),
    slippage_pct=np.array([np.nan]),
    status=np.array([np.nan]),
    status_info=np.array([np.nan]),
    tp_pcts=np.array([np.nan]),
    tp_prices=np.array([np.nan]),
    tsl_pcts=np.array([np.nan]),
    tsl_prices=np.array([np.nan]),
) -> OrderEverything:
    """
    This is where you put in all the parameters for creating your order.
    See [Order][quantfreedom.backtester.enums.enums.OrderEverything] for information on each parameter.
    """
    # run a for loop checking to see if something is an array or not ... if it isn't turn it into an array and if it is then leave it alone

    return OrderEverything(
        # required
        lev_mode=lev_mode,
        order_type=order_type,
        size_type=size_type,
        # not required
        allow_partial=allow_partial,
        available_balance=available_balance,
        average_entry=average_entry,
        cash_borrowed=cash_borrowed,
        cash_used=cash_used,
        equity=equity,
        fee=fee,
        fees_paid=fees_paid,
        leverage=leverage,
        liq_price=liq_price,
        log=log,
        max_equity_risk=max_equity_risk,
        max_equity_risk_pct=max_equity_risk_pct,
        max_lev=max_lev,
        max_order_pct_size=max_order_pct_size,
        max_order_size=max_order_size,
        min_order_pct_size=min_order_pct_size,
        min_order_size=min_order_size,
        mmr=mmr,
        pct_chg=pct_chg,
        position=position,
        raise_reject=raise_reject,
        realized_pnl=realized_pnl,
        reject_prob=reject_prob,
        risk_rewards=risk_rewards,
        size=size,
        size_pct=size_pct,
        sl_pcts=sl_pcts,
        sl_prices=sl_prices,
        slippage_pct=slippage_pct,
        status=status,
        status_info=status_info,
        tp_pcts=tp_pcts,
        tp_prices=tp_prices,
        tsl_pcts=tsl_pcts,
        tsl_prices=tsl_prices,
    )


@njit(cache=True)
def order_checker_nb(
    price: float,
    order: OrderEverything,
    account_state: AccountAndTradeState,
) -> tp.Tuple[AccountAndTradeState, OrderEverything]:
    """
    This goes through and checks your order for all types of different value errors.

    Args:
        order: See [Order][quantfreedom.backtester.enums.enums.OrderEverything].

        account_state: See [Account_State][quantfreedom.backtester.enums.enums.AccountAndTradeState].

    It also sets the leverage and size for specific size_types

    !!! note
        All math is based on bybit pnl calculations and order cost and everything. You can see everything
        [here](https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_SubCategories?id=a005g000031FzWkAAK&language=en_US&subTopic=USDT_Perpetual_Contract)
    """

    ''' ############################## Account ############################## '''
    ''' ############################## Account ############################## '''
    ''' ############################## Account ############################## '''
    ''' ############################## Account ############################## '''

    # Lets see if you even have any money
    if account_state.available_balance < 0 or not np.isfinite(account_state.available_balance) or (
            not np.isfinite(account_state.equity)) or account_state.equity <= 0:
        raise ValueError("YOU HAVE NO MONEY!!!! You Broke!!!!")

    if not np.isfinite(account_state.fee):
        raise ValueError("account_state.fee must be finite")

    if not np.isfinite(account_state.mmr):
        raise ValueError("account_state.mmr must be finite")

    ''' ############################## Position ############################## '''
    ''' ############################## Position ############################## '''
    ''' ############################## Position ############################## '''
    ''' ############################## Position ############################## '''

    # Are we even in a position?
    if account_state.position < 0:
        raise RejectedOrderError("You aren't in a position")

    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''

    if order.size < 1:
        raise ValueError("order.size must be greater than 1.")

    if not np.isfinite(order.min_order_size) or order.min_order_size < 1:
        raise ValueError(
            "order.min_order_size must be finite or 0 or greater")

    if np.isnan(order.max_order_size) or order.max_order_size < 1:
        raise ValueError("order.max_order_size must be greater than 1")

    if order.size < order.min_order_size:
        raise ValueError("Size is less than min order size")

    if order.size > order.max_order_size:
        raise ValueError("Size is greater than max order size")

    ''' ############################## Order Size pct ############################## '''
    ''' ############################## Order Size pct ############################## '''
    ''' ############################## Order Size pct ############################## '''
    ''' ############################## Order Size pct ############################## '''

    if np.isinf(order.size_pct) or order.size_pct <= 0:
        raise ValueError("order.size_pct must not be inf or greater than 0.")

    if not np.isfinite(order.min_order_pct_size) or order.min_order_pct_size < 0:
        raise ValueError(
            "order.min_order_pct_size must be finite or greater than zero")

    if np.isnan(order.max_order_pct_size) or order.max_order_pct_size < 0:
        raise ValueError("order.max_order_pct_size must be greater than 0")

    if order.size_pct < order.min_order_pct_size:
        raise ValueError("size_pct is less than min order pct size")

    if order.size_pct > order.max_order_pct_size:
        raise ValueError("size_pct is greater than max order pct size")

    ''' ############################## price ############################## '''
    ''' ############################## price ############################## '''
    ''' ############################## price ############################## '''
    ''' ############################## price ############################## '''

    if np.isinf(price) or price <= 0:
        raise ValueError("price must be np.nan or greater than 0")

    if np.isinf(order.slippage_pct) or order.slippage_pct < 0:
        raise ValueError(
            "order.slippage_pct must be np.nan or greater than zero")
    elif not np.isnan(order.slippage_pct):
        price = price * (1.0 + order.slippage_pct / 100)

    ''' ############################## Stops ############################## '''
    ''' ############################## Stops ############################## '''
    ''' ############################## Stops ############################## '''
    ''' ############################## Stops ############################## '''

    if np.isinf(order.sl_pcts) or order.sl_pcts < 0:
        raise ValueError(
            "sl_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(order.sl_prices) or order.sl_prices < 0:
        raise ValueError(
            "sl_prices has to be nan or greater than 0 and not inf")

    if np.isinf(order.tsl_pcts) or order.tsl_pcts < 0:
        raise ValueError(
            "tsl_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(order.tsl_prices) or order.tsl_prices < 0:
        raise ValueError(
            "tsl_prices has to be nan or greater than 0 and not inf")

    if np.isinf(order.tp_pcts) or order.tp_pcts < 0:
        raise ValueError(
            "tp_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(order.tp_pcts) or order.tp_pcts < 0:
        raise ValueError(
            "tp_pcts has to be nan or greater than 0 and not inf")

    check_sl_tsl_for_nan = (
        np.isnan(order.sl_pcts) and np.isnan(order.sl_prices) and (
            np.isnan(order.tsl_pcts) and np.isnan(order.tsl_prices)))

    ''' ############################## Leverage ############################## '''
    ''' ############################## Leverage ############################## '''
    ''' ############################## Leverage ############################## '''
    ''' ############################## Leverage ############################## '''

    # checking if leverage mode is out of range
    if (0 > order.lev_mode > len(LeverageMode)) or np.isinf(order.lev_mode):
        raise ValueError("Leverage mode is out of range or inf")

    # if leverage is too big or too small
    if order.lev_mode == LeverageMode.Isolated:
        if not np.isfinite(order.leverage) or 1 > order.leverage > order.max_lev:
            raise ValueError("Leverage needs to be between 1 and max lev")
        else:
            new_leverage = order.leverage

    # checking to make sure you have a sl or tsl with least free cash used
    elif order.lev_mode == LeverageMode.LeastFreeCashUsed:
        if check_sl_tsl_for_nan:
            raise RejectedOrderError(
                "When using Least Free Cash Used set a proper sl or tsl > 0")
        else:
            new_leverage = np.nan
    else:
        new_leverage = np.nan

    ''' ############################## Risk Reward ############################## '''
    ''' ############################## Risk Reward ############################## '''
    ''' ############################## Risk Reward ############################## '''
    ''' ############################## Risk Reward ############################## '''

    # making sure we have a number greater than 0 for rr
    if np.isinf(order.risk_rewards) or order.risk_rewards < 0:
        raise ValueError(
            "Risk Rewards has to be greater than 0 or np.nan")

    # check if RR has sl pct / price or tsl pct / price
    elif not np.isnan(order.risk_rewards) and check_sl_tsl_for_nan:
        raise RejectedOrderError(
            "When risk to reward is set you have to have a sl or tsl > 0")

    elif order.risk_rewards > 0 and (order.tp_pcts > 0 or order.tp_prices > 0):
        raise RejectedOrderError(
            "You can't have take profits set when using Risk to reward")

    ''' ############################## Max Risk ############################## '''
    ''' ############################## Max Risk ############################## '''
    ''' ############################## Max Risk ############################## '''
    ''' ############################## Max Risk ############################## '''

    if np.isinf(order.max_equity_risk_pct) or order.max_equity_risk_pct < 0:
        raise ValueError(
            "Max equity risk percent has to be greater than 0 or np.nan")
    elif np.isinf(order.max_equity_risk) or order.max_equity_risk < 0:
        raise ValueError("Max equity risk has to be greater than 0 or np.nan")

    ''' ############################## Two conflicting settings ############################## '''
    ''' ############################## Two conflicting settings ############################## '''
    ''' ############################## Two conflicting settings ############################## '''
    ''' ############################## Two conflicting settings ############################## '''

    if not np.isnan(order.max_equity_risk_pct) and not np.isnan(order.max_equity_risk):
        raise ValueError(
            "You can't have max risk pct and max risk both set at the same time.")
    elif not np.isnan(order.sl_pcts) and not np.isnan(order.sl_prices):
        raise ValueError(
            "You can't have sl pct and sl price both set at the same time.")
    elif not np.isnan(order.tsl_pcts) and not np.isnan(order.tsl_prices):
        raise ValueError(
            "You can't have tsl pct and tsl price both set at the same time.")
    elif not np.isnan(order.tp_pcts) and not np.isnan(order.tp_prices):
        raise ValueError(
            "You can't have tp pct and tp price both set at the same time.")
    elif not np.isnan(order.size) and not np.isnan(order.size_pct):
        raise ValueError(
            "You can't have size and size pct set at the same time.")

    ''' ############################## Setting Order Size or pct size Type ############################## '''
    ''' ############################## Setting Order Size or pct size Type ############################## '''
    ''' ############################## Setting Order Size or pct size Type ############################## '''
    ''' ############################## Setting Order Size or pct size Type ############################## '''

    # simple check if order size type is valid
    if 0 > order.order_type > len(OrderType) or not np.isfinite(order.order_type):
        raise ValueError("order.size_type is invalid")

    # Getting the right size for Size Type Amount
    if order.size_type == SizeType.Amount:
        size = order.size
        if size < 1:
            raise ValueError("With SizeType as amount, size 1 or greater.")
        elif size > order.max_order_size:
            if order.allow_partial != 1.:
                raise ValueError(
                    "With SizeType as amount, size is bigger than max size with partial not allowed.")
            size = order.max_order_size
        elif size == np.inf:
            size = account_state.position
        new_size_pct = np.nan

    # getting size for percent of account
    elif order.size_type == SizeType.PercentOfAccount:
        if np.isnan(order.size_pct):
            raise ValueError(
                "You need size_pct to be > 0 if using percent of account.")
        else:
            size = account_state.equity * \
                (order.size_pct / 100)  # math checked
            new_size_pct = order.size_pct

    # checking to see if you set a stop loss for risk based size types
    elif order.size_type == SizeType.RiskAmount or (
            order.size_type == SizeType.RiskPercentOfAccount) and check_sl_tsl_for_nan:
        raise ValueError(
            "When using Risk Amount or Risk Percent of Account set a proper sl or tsl > 0")

    # setting risk amount size
    elif order.size_type == SizeType.RiskAmount:
        size = order.size / (order.sl_pcts / 100)
        if size < 1:
            raise ValueError(
                "Risk Amount has produced a size values less than 1.")
        new_size_pct = np.nan

    # setting risk percent size
    elif order.size_type == SizeType.RiskPercentOfAccount:
        if np.isnan(order.size_pct):
            raise ValueError(
                "You need size_pct to be > 0 if using risk percent of account.")
        # TODO need to check for avg entry for multiple sl and also check to see if it is a tsl
        else:
            # get size of account at risk 100 / .01 = 1
            account_at_risk = account_state.equity * (order.size_pct/100)
            # get size needed to risk account at risk 1 / .01 = 100
            size = account_at_risk / (order.sl_pcts / 100)
            new_size_pct = order.size_pct
    else:
        raise TypeError(
            "I have no clue what is wrong but something is wrong with making the size using size type")

    # create the right size if there is a sl pct or price
    is_entry = order.order_type == OrderType.LongEntry or \
        order.order_type == OrderType.ShortEntry
    if np.isfinite(order.sl_pcts) and is_entry:
        sl_prices = price - (price * order.sl_pcts / 100)
        possible_loss = size * (order.sl_pcts / 100)

        size = -possible_loss / \
            (((sl_prices/price) - 1) - (account_state.fee / 100) -
             ((sl_prices * (account_state.fee / 100))/price))

    elif np.isfinite(order.sl_prices) and is_entry:
        sl_prices = order.sl_prices
        sl_pcts = abs((price - sl_prices) / price) * 100
        possible_loss = size * (sl_pcts / 100)

        size = -possible_loss / \
            (((sl_prices/price) - 1) - (account_state.fee / 100) -
             ((sl_prices * (account_state.fee / 100))/price))

    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''

    if size < 1:
        raise ValueError("order.size must be greater than 1.")

    if size < order.min_order_size:
        raise ValueError("Size is less than min order size")

    if size > order.max_order_size:
        raise ValueError("Size is greater than max order size")

    new_order = OrderEverything(
        # required
        lev_mode=order.lev_mode,
        order_type=order.order_type,
        size_type=order.size_type,
        # not required
        allow_partial=order.allow_partial,
        available_balance=account_state.available_balance,
        average_entry=account_state.average_entry,
        cash_borrowed=account_state.cash_borrowed,
        cash_used=account_state.cash_used,
        equity=account_state.equity,
        fee=account_state.fee,
        fees_paid=order.fees_paid,
        leverage=new_leverage,
        liq_price=account_state.liq_price,
        log=order.log,
        max_equity_risk=order.max_equity_risk,
        max_equity_risk_pct=order.max_equity_risk_pct,
        max_lev=order.max_lev,
        max_order_pct_size=order.max_order_pct_size,
        max_order_size=order.max_order_size,
        min_order_pct_size=order.min_order_pct_size,
        min_order_size=order.min_order_size,
        mmr=account_state.mmr,
        pct_chg=order.pct_chg,
        position=account_state.position,
        raise_reject=order.raise_reject,
        realized_pnl=account_state.realized_pnl,
        reject_prob=order.reject_prob,
        risk_rewards=order.risk_rewards,
        size=size,
        size_pct=new_size_pct,
        sl_pcts=order.sl_pcts,
        sl_prices=order.sl_prices,
        slippage_pct=order.slippage_pct,
        status=OrderStatus.Filled,
        status_info=OrderStatusInfo.HopefullyNoProblems,
        tp_pcts=order.tp_pcts,
        tp_prices=order.tp_prices,
        tsl_pcts=order.tsl_pcts,
        tsl_prices=order.tsl_prices,
    )

    new_account_state = AccountAndTradeState(
        available_balance=account_state.available_balance,
        average_entry=account_state.average_entry,
        cash_borrowed=account_state.cash_borrowed,
        cash_used=account_state.cash_used,
        equity=account_state.equity,
        fee=account_state.fee,
        leverage=new_leverage,
        liq_price=account_state.liq_price,
        mmr=account_state.mmr,
        position=account_state.position,
        realized_pnl=account_state.realized_pnl,
    )
    return new_account_state, new_order, price


@ njit(cache=True)
def execute_order_nb(
    price: float,
    order: OrderEverything,
    account_state: AccountAndTradeState,
) -> tp.Tuple[AccountAndTradeState, ResultEverything]:
    """
    It takes the order type and sends it to the proper place to get executed.

    Args:
        order: See [Order][quantfreedom.backtester.enums.enums.OrderEverything].

        account_state: See [Account_State][quantfreedom.backtester.enums.enums.AccountAndTradeState].
    """
    # Lets Long this thang!!!!!
    if order.order_type == OrderType.LongEntry and not np.isnan(order.lev_mode):
        new_account_state, order_result = long_increase_nb(
            price=price,
            account_state=account_state,
            order=order,
        )

    # Are we trying to decrease a long?
    elif 1 <= order.order_type <= 4:
        new_account_state, order_result = long_decrease_nb(
            price=price,
            account_state=account_state,
            order=order,
        )

    # Man you know you shouldn't short
    elif order.order_type == OrderType.ShortEntry and not np.isnan(order.lev_mode):
        new_account_state, order_result = short_increase_nb(
            price=price,
            account_state=account_state,
            order=order,
        )

    # Get me out of this short position NOW!!!!
    elif 6 <= order.order_type <= 9:
        new_account_state, order_result = short_decrease_nb(
            price=price,
            account_state=account_state,
            order=order,
        )

    # Somehow something went wrong
    else:
        raise RejectedOrderError(
            "execute_order_nb Lev mode is nan or something is wrong in choosing to long or short.")

    return new_account_state, order_result


@njit(cache=True)
def process_order_nb(
    price: float,
    bar: int,
    col: int,
    order: OrderEverything,
    account_state: AccountAndTradeState,
    order_records: tp.RecordArray,
    log_records: tp.Optional[tp.RecordArray] = None,
    group: int = 0,
) -> tp.Tuple[AccountAndTradeState, ResultEverything]:
    """
    Process an order by executing it, saving relevant information to the logs.
    Then returning a new account_state and order result

    Args:
        bar: The current bar you are at in the loop of the coin (col).
        col: col usually represents the number of which coin you are in. \
        So lets say you are testing BTC and ETH, BTC would be col 0 and ETH would be col 1.
        order: See [Order][quantfreedom.backtester.enums.enums.OrderEverything].
        account_state: See [Account_State][quantfreedom.backtester.enums.enums.AccountAndTradeState].
        order_records: See [Order Numpy Data Type][quantfreedom.backtester.enums.enums.order_dt].
        log_records: See [Log Numpy Data Type][quantfreedom.backtester.enums.enums.log_dt].
        group: If you group up your coins or anything else this will keep track of the group you are in.
    """
    # Check the order for errors and other things
    checked_account_state, checked_order, price = order_checker_nb(
        account_state=account_state, order=order, price=price)

    # Execute the order
    new_account_state, order_result = execute_order_nb(
        account_state=checked_account_state, 
        order=checked_order, 
        price=price)

    # Raise if order rejected
    is_rejected = order_result.status == OrderStatus.Rejected
    if is_rejected and order.raise_reject == 1.:
        raise_rejected_order_nb(order=order)

    new_order_count_id = account_state.order_count_id
    new_log_count_id = account_state.log_count_id

    # Start the order filling process
    is_filled = order_result.status == OrderStatus.Filled
    if order_records is not None and new_order_count_id is not None:
        if is_filled:
            # Fill order record
            fill_order_records_nb(
                order_records=order_records,
                order_count_id=new_order_count_id,
                bar=bar,
                col=col,
                group=group,
                order_result=order_result,
            )
            new_order_count_id += 1

    # Start the order filling process
    if log_records is not None and new_log_count_id is not None:
        if order.log == 1.:
            # Fill order record
            fill_log_records_nb(
                log_records=log_records,
                log_count_id=new_log_count_id,
                bar=bar,
                col=col,
                group=group,
                order_result=order_result,
                account_state=account_state,
                new_account_state=new_account_state,
                order_count_id=account_state.order_count_id
            )
            new_log_count_id += 1

    new_account_state = AccountAndTradeState(
        available_balance=new_account_state.available_balance,
        average_entry=new_account_state.average_entry,
        cash_borrowed=new_account_state.cash_borrowed,
        cash_used=new_account_state.cash_used,
        equity=new_account_state.equity,
        fee=new_account_state.fee,
        leverage=new_account_state.leverage,
        liq_price=new_account_state.liq_price,
        mmr=new_account_state.mmr,
        position=new_account_state.position,
        realized_pnl=new_account_state.realized_pnl,
        order_count_id=new_order_count_id,
        log_count_id=new_log_count_id,
    )

    return new_account_state, order_result


@njit(cache=True)
def simulate_only_1(
    open: tp.ArrayLike,
    high: tp.ArrayLike,
    low: tp.ArrayLike,
    close: tp.ArrayLike,
    entries: tp.ArrayLike,
    order: OrderEverything,
    account_state: AccountAndTradeState,
) -> tp.Tuple[tp.RecordArray, tp.RecordArray]:

    order_records = np.empty(open.shape[0], dtype=order_dt)
    log_records = np.empty(open.shape[0], dtype=log_dt)
    total_bars = open.shape[0]

    # for bar in range(open.shape[0]):
    for bar in range(total_bars):
        if entries[bar]:
            order = order_nb(
                # required
                lev_mode=order.lev_mode,
                order_type=order.order_type,
                price=open[bar],
                size_type=order.size_type,
                # not required
                allow_partial=order.allow_partial,
                available_balance=account_state.available_balance,
                average_entry=account_state.average_entry,
                cash_borrowed=account_state.cash_borrowed,
                cash_used=account_state.cash_used,
                equity=account_state.equity,
                fee=account_state.fee,
                fees_paid=order.fees_paid,
                leverage=account_state.leverage,
                liq_price=account_state.liq_price,
                log=order.log,
                max_equity_risk=order.max_equity_risk,
                max_equity_risk_pct=order.max_equity_risk_pct,
                max_lev=order.max_lev,
                max_order_pct_size=order.max_order_pct_size,
                max_order_size=order.max_order_size,
                min_order_pct_size=order.min_order_pct_size,
                min_order_size=order.min_order_size,
                mmr=account_state.mmr,
                pct_chg=order.pct_chg,
                position=order.position,
                raise_reject=order.raise_reject,
                realized_pnl=order.realized_pnl,
                reject_prob=order.reject_prob,
                risk_rewards=order.risk_rewards,
                size=order.size,
                size_pct=order.size_pct,
                sl_pcts=order.sl_pcts,
                sl_prices=order.sl_prices,
                slippage_pct=order.slippage_pct,
                status=order.status,
                status_info=order.status_info,
                tp_pcts=order.tp_pcts,
                tp_prices=order.tp_prices,
                tsl_pcts=order.tsl_pcts,
                tsl_prices=order.tsl_prices,
            )
            account_state, order_result = process_order_nb(
                bar=bar,
                col=0,
                group=0,
                account_state=account_state,
                order=order,
                order_records=order_records,
                log_records=log_records,
            )
        if account_state.position > 0:
            order_tp_sl = check_sl_tp_nb(high[bar], low[bar], order_result)
            if not np.isnan(order_tp_sl.size):
                account_state, _ = process_order_nb(
                    bar=bar,
                    col=0,
                    group=0,
                    account_state=account_state,
                    order=order_tp_sl,
                    order_records=order_records,
                    log_records=log_records,
                )

    return order_records[: account_state.order_count_id], log_records[: account_state.log_count_id]
