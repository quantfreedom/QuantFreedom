from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.api import API


class UMFutures(API):
    def __init__(self, key=None, secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = "https://fapi.binance.com"
        super().__init__(key, secret, **kwargs)

    # MARKETS
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import ping
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import time
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import exchange_info
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import depth
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import trades
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import historical_trades
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import agg_trades
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import klines
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import continuous_klines
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import index_price_klines
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import mark_price_klines
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import mark_price
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import funding_rate
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import (
        ticker_24hr_price_change,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import ticker_price
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import book_ticker
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import open_interest
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import open_interest_hist
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import (
        top_long_short_position_ratio,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import (
        long_short_account_ratio,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import (
        top_long_short_account_ratio,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import (
        taker_long_short_ratio,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import blvt_kline
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import index_info
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.market import asset_Index

    # ACCOUNT(including orders and trades)
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        change_position_mode,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import get_position_mode
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        change_multi_asset_mode,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        get_multi_asset_mode,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import new_order
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import new_order_test
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import modify_order
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import new_batch_order
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import query_order
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import cancel_order
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        cancel_open_orders,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        cancel_batch_order,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        countdown_cancel_order,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import get_open_orders
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import get_orders
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import get_all_orders
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import balance
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import account
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import change_leverage
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        change_margin_type,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        modify_isolated_position_margin,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        get_position_margin_history,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import get_position_risk
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        get_account_trades,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        get_income_history,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import leverage_brackets
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import adl_quantile
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import force_orders
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        api_trading_status,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import commission_rate
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        download_transactions_asyn,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.account import (
        aysnc_download_info,
    )

    # STREAMS
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.data_stream import (
        new_listen_key,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.data_stream import (
        renew_listen_key,
    )
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.data_stream import (
        close_listen_key,
    )

    # PORTFOLIO MARGIN
    from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures.portfolio_margin import (
        pm_exchange_info,
    )
