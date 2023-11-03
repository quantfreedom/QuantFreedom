import logging
import os
from time import sleep
from quantfreedom.email_sender import EmailSender
from quantfreedom.enums import (
    CandleBodyType,
    DynamicOrderSettings,
    IncreasePositionType,
    LeverageStrategyType,
    LoggerFuncType,
    LongOrShortType,
    MoveStopLoss,
    OrderPlacementType,
    PositionModeType,
    PriceGetterType,
    RejectedOrder,
    StaticOrderSettings,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
    ZeroOrEntryType,
)
from quantfreedom.order_handler.decrease_position import decrease_position
from quantfreedom.order_handler.increase_position import AccExOther, OrderInfo, long_min_amount, long_rpa_slbcb
from quantfreedom.order_handler.take_profit import long_c_tp_hit_regular, long_tp_rr
from quantfreedom.order_handler.leverage import long_check_liq_hit, long_dynamic_lev, long_static_lev
from quantfreedom.helper_funcs import (
    max_price_getter,
    min_price_getter,
    sl_to_entry,
    sl_to_z_e_pass,
    long_sl_to_zero,
)
from quantfreedom.order_handler.stop_loss import (
    long_c_sl_hit,
    long_cm_sl_to_be,
    long_cm_sl_to_be_pass,
    long_cm_tsl,
    long_cm_tsl_pass,
    long_sl_bcb,
    move_stop_loss,
    move_stop_loss_pass,
)
from quantfreedom.exchanges.live_exchange import LiveExchange
from datetime import datetime, timedelta
from dash_bootstrap_templates import load_figure_template
from jupyter_dash import JupyterDash
from dash import Dash
from IPython import get_ipython
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

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

trade_logger = logging.getLogger("trade")


class LiveTrading:
    ex_position_size_usd = 0
    ex_average_entry = 0
    last_pnl = 0
    order_available_balance = 0
    order_average_entry = 0
    order_cash_borrowed = 0
    order_cash_used = 0
    order_entry_price = 0
    order_entry_size_asset = 0
    order_entry_size_usd = 0
    order_equity = 0
    order_position_size_asset = 0
    order_sl_price = 0
    order_total_trades = 0
    order_possible_loss = 0

    def __init__(
        self,
        dynamic_order_settings: DynamicOrderSettings,
        email_sender: EmailSender,
        entry_order_type: OrderPlacementType,
        evaluate,
        exchange: LiveExchange,
        get_strategy_plot_filename,
        ind_creator,
        indicator_settings,
        logger: list,
        static_os: StaticOrderSettings,
        stringer: list,
        tp_order_type: OrderPlacementType,
    ):
        self.evaluate = evaluate
        self.ind_creator = ind_creator
        self.dynamic_order_settings = dynamic_order_settings
        self.exchange = exchange
        self.email_sender = email_sender
        self.symbol = self.exchange.symbol
        self.stringer: list = stringer
        self.logger: list = logger
        self.indicator_settings = indicator_settings
        self.get_strategy_plot_filename = get_strategy_plot_filename

        if self.exchange.position_mode == PositionModeType.HedgeMode:
            if self.exchange.long_or_short == LongOrShortType.Long:
                self.place_sl_order = self.exchange.create_long_hedge_mode_sl_order
                self.get_position_info = self.exchange.get_long_hedge_mode_position_info
                if entry_order_type == OrderPlacementType.Market:
                    self.entry_order = self.exchange.create_long_hedge_mode_entry_market_order

                if tp_order_type == OrderPlacementType.Market:
                    pass
                else:
                    self.place_tp_order = self.exchange.create_long_hedge_mode_tp_limit_order

        self.ex_position_size_asset = float(self.get_position_info().get("size"))
        self.order_equity = self.exchange.get_equity_of_asset(trading_in=self.exchange.trading_in)

        """
        #########################################
        #########################################
        #########################################
                        Trading
                        Trading
                        Trading
        #########################################
        #########################################
        #########################################
        """
        if static_os.long_or_short == LongOrShortType.Long:
            # Decrease Position
            self.dec_pos_calculator = decrease_position

            """
            #########################################
            #########################################
            #########################################
                            Stop Loss
                            Stop Loss
                            Stop Loss
            #########################################
            #########################################
            #########################################
            """

            # stop loss calulator
            if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
                self.sl_calculator = long_sl_bcb
                self.checker_sl_hit = long_c_sl_hit
                if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
                    self.sl_bcb_price_getter = min_price_getter
                elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
                    self.sl_bcb_price_getter = max_price_getter

            # SL break even
            if static_os.sl_to_be_bool:
                self.checker_sl_to_be = long_cm_sl_to_be
                # setting up stop loss be zero or entry
                if static_os.z_or_e_type == ZeroOrEntryType.ZeroLoss:
                    self.zero_or_entry_calc = long_sl_to_zero
                elif static_os.z_or_e_type == ZeroOrEntryType.AverageEntry:
                    self.zero_or_entry_calc = sl_to_entry
            else:
                self.checker_sl_to_be = long_cm_sl_to_be_pass
                self.zero_or_entry_calc = sl_to_z_e_pass

            # Trailing stop loss
            if static_os.trail_sl_bool:
                self.checker_tsl = long_cm_tsl
            else:
                self.checker_tsl = long_cm_tsl_pass

            if static_os.trail_sl_bool or static_os.sl_to_be_bool:
                self.sl_mover = move_stop_loss
            else:
                self.sl_mover = move_stop_loss_pass

            """
            #########################################
            #########################################
            #########################################
                        Increase position
                        Increase position
                        Increase position
            #########################################
            #########################################
            #########################################
            """

            if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
                if static_os.increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                    self.inc_pos_calculator = long_rpa_slbcb

                elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
                    self.inc_pos_calculator = long_min_amount

            """
            #########################################
            #########################################
            #########################################
                            Leverage
                            Leverage
                            Leverage
            #########################################
            #########################################
            #########################################
            """

            if static_os.leverage_strategy_type == LeverageStrategyType.Dynamic:
                self.lev_calculator = long_dynamic_lev
            else:
                self.lev_calculator = long_static_lev

            self.checker_liq_hit = long_check_liq_hit
            """
            #########################################
            #########################################
            #########################################
                            Take Profit
                            Take Profit
                            Take Profit
            #########################################
            #########################################
            #########################################
            """

            if static_os.tp_strategy_type == TakeProfitStrategyType.RiskReward:
                self.tp_calculator = long_tp_rr
                self.checker_tp_hit = long_c_tp_hit_regular
            elif static_os.tp_strategy_type == TakeProfitStrategyType.Provided:
                pass
        """
        #########################################
        #########################################
        #########################################
                    Other Settings
                    Other Settings
                    Other Settings
        #########################################
        #########################################
        #########################################
        """

        if static_os.tp_fee_type == TakeProfitFeeType.Market:
            self.exit_fee_pct = exchange.exchange_settings.market_fee_pct
        else:
            self.exit_fee_pct = exchange.exchange_settings.limit_fee_pct
        """
        #########################################
        #########################################
        #########################################
                    End User Setup
                    End User Setup
                    End User Setup
        #########################################
        #########################################
        #########################################
        """

    def pass_function(self, **vargs):
        pass

    def run(self):
        max_equity_risk_pct = self.dynamic_order_settings.max_equity_risk_pct
        max_trades = self.dynamic_order_settings.max_trades
        risk_account_pct_size = self.dynamic_order_settings.risk_account_pct_size
        risk_reward = self.dynamic_order_settings.risk_reward
        sl_based_on_add_pct = self.dynamic_order_settings.sl_based_on_add_pct
        sl_based_on_lookback = self.dynamic_order_settings.sl_based_on_lookback
        sl_bcb_type = self.dynamic_order_settings.sl_bcb_type
        sl_to_be_cb_type = self.dynamic_order_settings.sl_to_be_cb_type
        sl_to_be_when_pct = self.dynamic_order_settings.sl_to_be_when_pct
        static_leverage = self.dynamic_order_settings.static_leverage
        trail_sl_bcb_type = self.dynamic_order_settings.trail_sl_bcb_type
        trail_sl_by_pct = self.dynamic_order_settings.trail_sl_by_pct
        trail_sl_when_pct = self.dynamic_order_settings.trail_sl_when_pct

        asset_tick_step = self.exchange.exchange_settings.asset_tick_step
        leverage_tick_step = self.exchange.exchange_settings.leverage_tick_step
        market_fee_pct = self.exchange.exchange_settings.market_fee_pct
        max_asset_size = self.exchange.exchange_settings.max_asset_size
        max_leverage = self.exchange.exchange_settings.max_leverage
        min_asset_size = self.exchange.exchange_settings.min_asset_size
        min_leverage = self.exchange.exchange_settings.min_leverage
        mmr_pct = self.exchange.exchange_settings.mmr_pct
        price_tick_step = self.exchange.exchange_settings.price_tick_step

        latest_pnl = 0

        self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Starting live trading")
        print(f"Starting live trading")
        try:
            self.last_pnl = self.exchange.get_latest_pnl_result(symbol=self.symbol)
        except Exception as e:
            self.logger[LoggerFuncType.Warning](f"live_mode.py - run() - get_latest_pnl_result {e}")
            pass
        entry_order_id = 0
        tp_order_id = 0
        sl_order_id = 0

        self.exchange.set_init_last_fetched_time()
        self.logger[LoggerFuncType.Info](
            f"live_mode.py - run() - Last Candle time {self.exchange.last_fetched_time_to_pd_datetime()}"
        )
        sleep(self.get_sleep_time_to_next_bar())
        while True:
            try:
                self.logger[LoggerFuncType.Info]("live_mode.py - run() - Getting Candles")
                print("Getting Candles")
                self.candles = self.exchange.get_live_candles()
                num_candles = self.candles.shape[0]

                # bar_index bar index is always the last bar ... so if we have 200 candles we are at index 200
                bar_index = num_candles - 1
                msg = "Couldn't verify that the following orders were placed "

                self.logger[LoggerFuncType.Debug]("live_mode.py - run() - Setting indicator")
                try:
                    latest_pnl = self.exchange.get_latest_pnl_result(symbol=self.symbol)
                except Exception as e:
                    self.logger[LoggerFuncType.Warning](f"live_mode.py - run() - get_latest_pnl_result {e}")
                self.logger[LoggerFuncType.Info]("live_mode.py - run() - Evaluating Strat")
                if self.evaluate(
                    bar_index=0,
                    starting_bar=0,
                    candles=self.candles,
                    indicator_settings=self.indicator_settings,
                    ind_creator=self.ind_creator,
                    logger=self.logger,
                    stringer=self.stringer,
                ):
                    try:
                        self.logger[LoggerFuncType.Debug]("live_mode.py - run() - Setting ex postion size usd")
                        self.__set_ex_position_size_usd()
                        if self.ex_position_size_usd > 0:
                            self.logger[LoggerFuncType.Debug](
                                "live_mode.py - run() - We are in a position updating order info"
                            )
                            self.order_position_size_usd = self.ex_position_size_usd
                            self.__set_order_average_entry()
                        else:
                            self.logger[LoggerFuncType.Debug](
                                "live_mode.py - run() - we are not in a position updating order info"
                            )
                            self.order_position_size_usd = 0.0
                            self.order_average_entry = 0.0
                            self.order_equity = self.exchange.get_equity_of_asset(trading_in=self.exchange.trading_in)
                            self.order_available_balance = self.order_equity
                            self.order_possible_loss = 0.0
                            self.order_cash_used = 0.0
                            self.order_cach_borrowed = 0.0

                        self.order_sl_price = self.sl_calculator(
                            bar_index=num_candles,
                            candles=self.candles,
                            logger=self.logger,
                            stringer=self.stringer,
                            price_tick_step=price_tick_step,
                            sl_based_on_add_pct=sl_based_on_add_pct,
                            sl_based_on_lookback=sl_based_on_lookback,
                            sl_bcb_price_getter=self.sl_bcb_price_getter,
                            sl_bcb_type=sl_bcb_type,
                        )

                        (
                            self.order_average_entry,
                            self.order_entry_price,
                            self.order_entry_size_asset,
                            self.order_entry_size_usd,
                            self.order_position_size_asset,
                            self.order_position_size_usd,
                            self.order_possible_loss,
                            self.order_total_trades,
                            self.order_sl_pct,
                        ) = self.inc_pos_calculator(
                            acc_ex_other=AccExOther(
                                account_state_equity=self.order_equity,
                                asset_tick_step=asset_tick_step,
                                market_fee_pct=market_fee_pct,
                                max_asset_size=max_asset_size,
                                min_asset_size=min_asset_size,
                                possible_loss=self.order_possible_loss,
                                price_tick_step=price_tick_step,
                                total_trades=self.order_total_trades,
                            ),
                            order_info=OrderInfo(
                                average_entry=self.order_average_entry,
                                entry_price=self.candles[-1, CandleBodyType.Close],
                                in_position=self.order_position_size_usd > 0,
                                max_equity_risk_pct=max_equity_risk_pct,
                                max_trades=max_trades,
                                position_size_asset=self.order_position_size_asset,
                                position_size_usd=self.order_position_size_usd,
                                risk_account_pct_size=risk_account_pct_size,
                                sl_price=self.order_sl_price,
                            ),
                            logger=self.logger,
                            stringer=self.stringer,
                        )
                        self.logger[LoggerFuncType.Debug]("live_mode.py - run() - calculate_leverage")
                        (
                            self.order_available_balance,
                            self.order_cash_borrowed,
                            self.order_cash_used,
                            self.order_leverage,
                            self.order_liq_price,
                        ) = self.lev_calculator(
                            available_balance=self.order_available_balance,
                            average_entry=self.order_average_entry,
                            cash_borrowed=self.order_cash_borrowed,
                            cash_used=self.order_cash_used,
                            entry_size_usd=self.order_entry_size_usd,
                            max_leverage=max_leverage,
                            min_leverage=min_leverage,
                            stringer=self.stringer,
                            mmr_pct=mmr_pct,
                            sl_price=self.order_sl_price,
                            static_leverage=static_leverage,
                            leverage_tick_step=leverage_tick_step,
                            price_tick_step=price_tick_step,
                            logger=self.logger,
                        )
                        self.logger[LoggerFuncType.Debug]("live_mode.py - run() - calculate_take_profit")
                        (
                            self.order_can_move_sl_to_be,
                            self.order_tp_price,
                            self.order_tp_pct,
                        ) = self.tp_calculator(
                            average_entry=self.order_average_entry,
                            market_fee_pct=market_fee_pct,
                            position_size_usd=self.order_position_size_usd,
                            possible_loss=self.order_possible_loss,
                            price_tick_step=price_tick_step,
                            risk_reward=risk_reward,
                            tp_fee_pct=self.exit_fee_pct,
                            stringer=self.stringer,
                            logger=self.logger,
                        )

                        # place the order
                        send_verify_error = False
                        self.logger[LoggerFuncType.Info]("live_mode.py - run() - Placing Entry Order")
                        entry_order_id = self.entry_order(
                            asset_amount=self.order_entry_size_asset,
                            entry_price=self.order_entry_price,
                        )

                        self.logger[LoggerFuncType.Info](
                            f"live_mode.py - run() - Submitted entry order -> [order_id={entry_order_id}]"
                        )
                        sleep(0.5)

                        # check if order fileld
                        self.logger[LoggerFuncType.Debug](f"live_mode.py - run() - Checking if entry order was filled")
                        if self.exchange.check_if_order_filled(
                            symbol=self.symbol,
                            order_id=entry_order_id,
                        ):
                            self.logger[LoggerFuncType.Info]("live_mode.py - run() - Entry was filled")
                        else:
                            msg += f"entry_order_id {entry_order_id} "
                            send_verify_error = True
                            self.logger[LoggerFuncType.Warning](
                                f"live_mode.py - run() - Couldn't verify entry order was filled {entry_order_id}"
                            )

                        # cancel other orders if in position
                        self.logger[LoggerFuncType.Info](
                            f"live_mode.py - run() - checking if in position to cancel tp and sl"
                        )
                        self.__set_ex_position_size_asset()
                        if self.ex_position_size_asset > 0:
                            self.logger[LoggerFuncType.Info](
                                f"live_mode.py - run() - We are in a pos and trying to cancel tp and sl"
                            )
                            if self.exchange.cancel_all_open_order_per_symbol(symbol=self.symbol):
                                self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Canceled the orders")
                            else:
                                self.logger[LoggerFuncType.Warning](
                                    "live_mode.py - run() - Wasn't able to verify that the tp and sl were canceled"
                                )

                        sleep(0.5)

                        # set the levergae
                        self.logger[LoggerFuncType.Info]("live_mode.py - run() - Setting leverage")
                        if self.exchange.set_leverage_value(
                            symbol=self.symbol,
                            leverage=self.order_leverage,
                        ):
                            self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Leverage Changed")
                        else:
                            self.logger[LoggerFuncType.Warning](
                                "live_mode.py - run() - Couldn't verify that leverage was set"
                            )
                            msg += f"leverage was set "
                            send_verify_error = True

                        self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Submitting stop loss order")
                        sl_order_id = self.place_sl_order(
                            asset_amount=self.ex_position_size_asset,
                            trigger_price=self.order_sl_price,
                        )
                        self.logger[LoggerFuncType.Info](
                            f"live_mode.py - run() - Submitted SL order -> [order_id={sl_order_id}]"
                        )

                        sleep(0.5)
                        self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Submitting take profit order")
                        tp_order_id = self.place_tp_order(
                            asset_amount=self.ex_position_size_asset,
                            tp_price=self.order_tp_price,
                        )
                        self.logger[LoggerFuncType.Info](
                            f"live_mode.py - run() - Submitted TP order -> [order_id={tp_order_id}]"
                        )
                        market_fee_pct
                        # sleep 1 second before checking to see if orders were placed
                        sleep(1)
                        self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Checking if stop loss was placed")
                        if self.exchange.check_if_order_open(
                            symbol=self.symbol,
                            order_id=sl_order_id,
                        ):
                            self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Stop loss was placed")
                        else:
                            self.logger[LoggerFuncType.Warning](
                                f"live_mode.py - run() - Couldn't verify sl order was placed {sl_order_id} "
                            )
                            msg += f"sl_order_id {sl_order_id} "
                            send_verify_error = True

                        self.logger[LoggerFuncType.Debug](f"live_mode.py - run() - Checking if tp was placed")
                        if self.exchange.check_if_order_open(
                            symbol=self.symbol,
                            order_id=tp_order_id,
                        ):
                            self.logger[LoggerFuncType.Info](f"live_mode.py - run() - take profit placed")
                        else:
                            self.logger[LoggerFuncType.Info](
                                f"live_mode.py - run() - Couldn't verify tp order was filled {tp_order_id}"
                            )
                            msg += f"tp_order_id {tp_order_id}"
                            send_verify_error = True

                        if send_verify_error:
                            self.logger[LoggerFuncType.Info](
                                "live_mode.py - run() - Something wan't verified so rechecking all"
                            )
                            entry_placed = self.exchange.check_if_order_filled(
                                symbol=self.symbol,
                                order_id=entry_order_id,
                            )
                            leverage_changed = self.exchange.set_leverage_value(
                                symbol=self.symbol,
                                leverage=self.order_leverage,
                            )
                            sl_placed = self.exchange.check_if_order_open(
                                symbol=self.symbol,
                                order_id=sl_order_id,
                            )
                            tp_placed = self.exchange.check_if_order_open(
                                symbol=self.symbol,
                                order_id=tp_order_id,
                            )
                            verify_list = [entry_placed, leverage_changed, sl_placed, tp_placed]
                            if not all(v == True for v in verify_list):
                                self.logger[LoggerFuncType.Error](msg)
                                raise Exception(msg)
                            self.logger[LoggerFuncType.Info]("live_mode.py - run() - All verified")

                        else:
                            self.__set_exchange_variables(
                                entry_order_id=entry_order_id,
                                sl_order_id=sl_order_id,
                                tp_order_id=tp_order_id,
                            )
                            message = self.__create_entry_successful_message()
                            entry_filename = self.__get_entry_plot_filename()
                            strategy_filename = self.get_strategy_plot_filename(
                                bar_index=0,
                                starting_bar=0,
                                candles=self.candles,
                                indicator_settings=self.indicator_settings,
                                ind_creator=self.ind_creator,
                                logger=self.logger,
                            )
                            # self.email_sender.email_new_order(
                            #     message=message,
                            #     entry_filename=entry_filename,
                            #     strategy_filename=strategy_filename,
                            # )
                            self.logger[LoggerFuncType.Info]("live_mode.py - run() - Entry placed on exchange")
                            trade_logger.info(f"{message}")

                    except RejectedOrder as e:
                        self.logger[LoggerFuncType.Warning](f"live_mode.py - run() - RejectedOrder -> {e}")
                        pass
                    except Exception as e:
                        self.logger[LoggerFuncType.Error](f"live_mode.py - run() - Exception Entry -> {e}")
                        raise Exception(f"live_mode.py - run() - Exception Entry -> {e}")
                    self.__set_ex_position_size_asset()
                    if self.ex_position_size_asset > 0:
                        self.logger[LoggerFuncType.Info](
                            f"live_mode.py - run() - We are in a position ... checking to move stop loss"
                        )
                        try:
                            temp_sl = self.checker_sl_to_be(
                                average_entry=self.order_average_entry,
                                can_move_sl_to_be=self.order_can_move_sl_to_be,
                                candle_body_type=sl_to_be_cb_type,
                                current_candle=self.candles[bar_index, :],
                                logger=self.logger,
                                market_fee_pct=market_fee_pct,
                                price_tick_step=price_tick_step,
                                sl_price=self.order_sl_price,
                                sl_to_be_move_when_pct=sl_to_be_when_pct,
                                stringer=self.stringer,
                                zero_or_entry_calc=self.zero_or_entry_calc,
                            )
                            if temp_sl > 0:
                                if self.exchange.move_stop_order(
                                    symbol=self.symbol,
                                    order_id=sl_order_id,
                                    asset_amount=self.ex_position_size_asset,
                                    new_price=temp_sl,
                                ):
                                    self.logger[LoggerFuncType.Info](
                                        f"live_mode.py - run() - Moved stop loss from {self.order_sl_price:,} to {temp_sl:,}"
                                    )
                                    self.order_sl_price = temp_sl
                                else:
                                    self.logger[LoggerFuncType.Warning](
                                        f"live_mode.py - run() - Couldn't verify sl was moved {sl_order_id}"
                                    )
                                    raise Exception(f"live_mode.py - run() - Exception MoveStopLoss -> {e}")
                            else:
                                self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Wont move sl to be")
                            temp_tsl = self.checker_tsl(
                                average_entry=self.order_average_entry,
                                candle_body_type=trail_sl_bcb_type,
                                current_candle=self.candles[bar_index, :],
                                logger=self.logger,
                                price_tick_step=price_tick_step,
                                sl_price=self.order_sl_price,
                                stringer=self.stringer,
                                trail_sl_by_pct=trail_sl_by_pct,
                                trail_sl_when_pct=trail_sl_when_pct,
                            )
                            if temp_tsl > 0:
                                if self.exchange.move_stop_order(
                                    symbol=self.symbol,
                                    order_id=sl_order_id,
                                    asset_amount=self.ex_position_size_asset,
                                    new_price=temp_tsl,
                                ):
                                    self.logger[LoggerFuncType.Info](
                                        f"live_mode.py - run() - Moved stop loss from {self.order_sl_price:,} to {temp_tsl:,}"
                                    )
                                    self.order_sl_price = temp_tsl
                                else:
                                    self.logger[LoggerFuncType.Warning](
                                        f"live_mode.py - run() - Couldn't verify tsl was moved {sl_order_id}"
                                    )
                                    raise Exception(f"live_mode.py - run() - Exception Move TSL -> {e}")
                            else:
                                self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Wont move tsl")
                        except Exception as e:
                            self.logger[LoggerFuncType.Error](
                                f"live_mode.py - run() - Exception checking MoveStopLoss -> {e}"
                            )
                            raise Exception(f"live_mode.py - run() - Exception checking MoveStopLoss -> {e}")
                elif latest_pnl != self.last_pnl:
                    self.logger[LoggerFuncType.Info](f"live_mode.py - run() - Got a new pnl {latest_pnl}")
                    # self.email_sender.email_pnl(pnl=latest_pnl)
                    self.last_pnl = latest_pnl
                else:
                    pass
            except Exception as e:
                self.logger[LoggerFuncType.Error](f"live_mode.py - run() - Exception -> {e}")
                # self.email_sender.email_error_msg(msg=f"live_mode.py - run() - Exception -> {e}")
                raise Exception(f"live_mode.py - run() - Exception -> {e}")
            sleep(self.get_sleep_time_to_next_bar())

    def get_sleep_time_to_next_bar(self):
        ms_to_next_candle = max(
            0,
            (self.exchange.last_fetched_ms_time + self.exchange.timeframe_in_ms * 2)
            - self.exchange.get_current_time_ms(),
        )
        td = str(timedelta(seconds=ms_to_next_candle / 1000)).split(":")
        self.logger[LoggerFuncType.Info](
            f"live_mode.py - get_sleep_time_to_next_bar() - Will sleep for {td[0]} hrs {td[1]} mins and {td[2]} seconds till next bar\n"
        )
        print(f"Will sleep for {td[0]} hrs {td[1]} mins and {td[2]} seconds till next bar\n")

        return int(ms_to_next_candle / 1000)

    def __set_ex_position_size_asset(self):
        self.logger[LoggerFuncType.Debug](
            f"live_mode.py - __set_ex_position_size_asset() - Setting position size asset"
        )
        self.ex_position_size_asset = float(self.get_position_info()["size"])

    def __set_ex_position_size_usd(self):
        self.logger[LoggerFuncType.Debug](f"live_mode.py - __set_ex_position_size_usd() - Setting position size usd")
        self.ex_position_size_usd = float(self.get_position_info()["positionValue"])

    def __set_order_average_entry(self):
        self.logger[LoggerFuncType.Debug](f"live_mode.py - __set_order_average_entry() - Setting average entry")
        self.order_average_entry = float(self.get_position_info()["entryPrice"])

    def __set_ex_possible_loss(self):
        self.logger[LoggerFuncType.Debug](f"live_mode.py - __set_ex_possible_loss() - setting all exchange vars")
        coin_size = self.ex_position_size_asset
        pnl = coin_size * (self.ex_sl_price - self.ex_average_entry)
        fee_open = coin_size * self.ex_average_entry * self.exchange.exchange_settings.market_fee_pct  # math checked
        fee_close = coin_size * self.ex_sl_price * self.exchange.exchange_settings.market_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.ex_possible_loss = round(abs(pnl - self.fees_paid), 3)

    def __set_ex_possible_profit(self):
        self.logger[LoggerFuncType.Debug](f"live_mode.py - __set_ex_possible_profit() - setting all exchange vars")
        coin_size = self.ex_position_size_asset
        pnl = coin_size * (self.ex_tp_price - self.ex_average_entry)
        fee_open = coin_size * self.ex_average_entry * self.exchange.exchange_settings.market_fee_pct  # math checked
        fee_close = coin_size * self.ex_tp_price * self.exchange.exchange_settings.limit_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.ex_possible_profit = round(abs(pnl - self.fees_paid), 3)

    def __set_exchange_variables(self, entry_order_id, sl_order_id, tp_order_id):
        self.logger[LoggerFuncType.Debug](f"live_mode.py - __set_exchange_variables() - setting all exchange vars")
        pos_info = self.get_position_info()
        entry_info = self.exchange.get_filled_orders_by_order_id(symbol=self.symbol, order_id=entry_order_id)
        tp_info = self.exchange.get_open_order_by_order_id(symbol=self.symbol, order_id=tp_order_id)
        sl_info = self.exchange.get_open_order_by_order_id(symbol=self.symbol, order_id=sl_order_id)

        self.ex_position_size_asset = float(pos_info.get("size"))
        self.ex_position_size_usd = float(pos_info.get("positionValue"))
        self.ex_average_entry = float(pos_info.get("entryPrice"))
        self.avg_entry_slippage = self.__get_pct_difference(self.order_average_entry, self.ex_average_entry)
        self.ex_entry_price = float(entry_info.get("execPrice"))
        self.entry_slippage = self.__get_pct_difference(self.order_entry_price, self.ex_entry_price)
        self.ex_entry_size_asset = float(entry_info.get("execQty"))
        self.ex_entry_size_usd = float(entry_info.get("execValue"))
        self.ex_leverage = float(pos_info.get("leverage"))
        self.ex_liq_price = float(pos_info.get("liqPrice"))
        self.ex_liq_pct = self.__get_pct_difference(starting_num=self.ex_average_entry, diff_num=self.ex_liq_price)
        self.ex_tp_price = float(tp_info.get("price"))
        self.ex_tp_pct = self.__get_pct_difference(starting_num=self.ex_average_entry, diff_num=self.ex_tp_price)
        self.ex_sl_price = float(sl_info.get("triggerPrice"))
        self.ex_sl_pct = self.__get_pct_difference(starting_num=self.ex_average_entry, diff_num=self.ex_sl_price)
        coin_size = self.ex_position_size_asset
        pnl = coin_size * (self.ex_sl_price - self.ex_average_entry)
        fee_open = coin_size * self.ex_average_entry * self.exchange.exchange_settings.market_fee_pct  # math checked
        fee_close = coin_size * self.ex_sl_price * self.exchange.exchange_settings.market_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.ex_possible_loss = round(-(pnl - self.fees_paid), 3)

    def __get_pct_difference(self, starting_num, diff_num):
        self.logger[LoggerFuncType.Debug](f"live_mode.py - __get_pct_difference() - getting pct difference")
        return round(abs((starting_num - diff_num) / starting_num) * 100, 2)

    def __create_entry_successful_message(self):
        self.logger[LoggerFuncType.Debug](f"live_mode.py - __create_entry_successful_message() - Creating message")
        self.__set_ex_possible_loss()
        self.__set_ex_possible_profit()

        message = f"An order was placed successfully\n\
[ex_candle_closing_price={self.candles[-1,CandleBodyType.Close]:,}]\n\
[entry_price={self.order_entry_price:,}]\n\
[ex_entry_price={self.ex_entry_price:,}]\n\
[Entry slippage={self.entry_slippage}]\n\n\
[average_entry={self.order_average_entry:,}]\n\
[ex_average_entry={self.ex_average_entry:,}]\n\
[Average Entry slippage={self.avg_entry_slippage}]\n\n\
[position_size_usd={self.order_position_size_usd:,}]\n\
[ex_position_size_usd={self.ex_position_size_usd:,}]\n\n\
[entry_size_usd={self.order_entry_size_usd:,}]\n\
[ex_entry_size_usd={self.ex_entry_size_usd:,}]\n\n\
[leverage={self.order_leverage:,}]\n\
[ex_leverage={self.ex_leverage:,}]\n\n\
[liq price={self.order_liq_price:,}]\n\
[ex_liq price={self.ex_liq_price:,}]\n\
[ex_liq_pct={self.ex_liq_pct:,}]\n\n\
[candle low={self.candles[-1,CandleBodyType.Low]:,}]\n\
[stop_loss_price={self.order_sl_price:,}]\n\
[ex_stop_loss_price={self.ex_sl_price:,}]\n\
[ex_sl_pct={self.ex_sl_pct}]\n\n\
[take_profit_price={self.order_tp_price:,}]\n\
[ex_take_profit_price={self.ex_tp_price:,}]\n\n\
[ex_tp_pct={self.ex_tp_pct}]\n\n\
[possible loss={self.order_possible_loss:,}]\n\
[ex_possible loss={self.ex_possible_loss:,}]\n\
[ex_possible profit={self.ex_possible_profit:,}]\n"
        return message

    def __get_entry_plot_filename(self):
        self.logger[LoggerFuncType.Debug]("live_mode.py - __get_entry_plot_filename() - Getting entry plot file")
        last_20 = self.candles[-20:]
        last_20_datetimes = pd.to_datetime(last_20[:, CandleBodyType.Timestamp], unit="ms")
        graph_entry = [last_20_datetimes[-1]]
        fig = go.Figure()
        fig.add_candlestick(
            x=last_20_datetimes,
            open=last_20[:, CandleBodyType.Open],
            high=last_20[:, CandleBodyType.High],
            low=last_20[:, CandleBodyType.Low],
            close=last_20[:, CandleBodyType.Close],
            name="Exchange order",
        )
        # entry
        fig.add_scatter(
            x=graph_entry,
            y=[self.order_entry_price],
            mode="markers",
            marker=dict(size=10, color="LightSeaGreen"),
            name=f"Entry",
        )
        # average entry
        fig.add_scatter(
            x=graph_entry,
            y=[self.ex_average_entry],
            mode="markers",
            marker=dict(size=10, color="purple", symbol="arrow-up"),
            name=f"Average Entry",
        )
        # take profit
        fig.add_scatter(
            x=graph_entry,
            y=[self.ex_tp_price],
            mode="markers",
            marker=dict(size=10, symbol="star", color="Green"),
            name=f"Take Profit",
        )
        # stop loss
        fig.add_scatter(
            x=graph_entry,
            y=[self.ex_sl_price],
            mode="markers",
            marker=dict(size=10, symbol="x", color="orange"),
            name=f"Stop Loss",
        )
        # liq price
        fig.add_scatter(
            x=graph_entry,
            y=[self.ex_liq_price],
            mode="markers",
            marker=dict(size=10, symbol="hexagram", color="red"),
            name=f"Liq Price",
        )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()
        entry_filename = os.path.join(
            ".",
            "logs",
            "images",
            f'entry_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.png',
        )
        fig.write_image(entry_filename)
        return entry_filename
