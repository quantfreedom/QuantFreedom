import logging
import os
from time import sleep
from quantfreedom.email_sender import EmailSender
from quantfreedom.enums import (
    LongOrShortType,
    MoveStopLoss,
    OrderPlacementType,
    PositionModeType,
    RejectedOrder,
)
from quantfreedom.exchanges.live_exchange import LiveExchange
from quantfreedom.order_handler.order_handler import Order
from quantfreedom.strategy import Strategy
from datetime import datetime, timedelta
from dash_bootstrap_templates import load_figure_template
from jupyter_dash import JupyterDash
from dash import Dash
from IPython import get_ipython
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

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

info_logger = logging.getLogger("info")
trade_logger = logging.getLogger("trades")


class LiveTrading:
    ex_position_size_usd = 0
    ex_average_entry = 0

    def __init__(
        self,
        exchange: LiveExchange,
        strategy: Strategy,
        order: Order,
        entry_order_type: OrderPlacementType,
        tp_order_type: OrderPlacementType,
        email_sender: EmailSender,
    ):
        self.exchange = exchange
        self.strategy = strategy
        self.order = order
        self.email_sender = email_sender
        self.symbol = self.exchange.symbol

        if self.exchange.position_mode == PositionModeType.HedgeMode:
            if self.exchange.long_or_short == LongOrShortType.Long:
                self.place_sl_order = self.exchange.create_long_hedge_mode_sl_order
                self.get_position_info = self.exchange.get_long_hedge_mode_position_info
                self.get_tp_pct = self.__get_pct_dif_above_average_entry
                self.get_sl_pct = self.__get_pct_dif_below_average_entry
                self.get_liq_pct = self.__get_pct_dif_below_average_entry
                if entry_order_type == OrderPlacementType.Market:
                    self.entry_order = self.exchange.create_long_hedge_mode_entry_market_order

                if tp_order_type == OrderPlacementType.Market:
                    pass
                else:
                    self.place_tp_order = self.exchange.create_long_hedge_mode_tp_limit_order

        self.ex_position_size_asset = float(self.get_position_info().get("size"))
        self.order.equity = self.exchange.get_equity_of_asset(trading_in=self.exchange.trading_in)

    def pass_function(self, **vargs):
        pass

    def run(self):
        latest_pnl = 0
        self.last_pnl = 0
        info_logger.info(f"Starting live trading")
        print(f"Starting live trading")
        # self.last_pnl = self.exchange.get_latest_pnl_result(symbol=self.symbol)
        entry_order_id = 0
        tp_order_id = 0
        sl_order_id = 0

        self.exchange.set_init_last_fetched_time()
        info_logger.info(f"Last Candle time {self.exchange.last_fetched_time_to_pd_datetime()}")
        sleep(self.get_sleep_time_to_next_bar())
        while True:
            try:
                info_logger.info("Getting Candles")
                print("Getting Candles")
                self.exchange.set_candles_df_and_np()
                num_candles = self.exchange.candles_np.shape[0]

                # bar_index bar index is always the last bar ... so if we have 200 candles we are at index 200
                bar_index = num_candles - 1
                msg = "Couldn't verify that the following orders were placed "

                info_logger.debug("Setting indicator")
                self.strategy.set_indicator_live_trading(self.exchange.candles_df)
                # latest_pnl = self.exchange.get_latest_pnl_result(symbol=self.symbol)
                info_logger.info("Evaluating Strat")
                if self.strategy.evaluate():
                    try:
                        info_logger.debug("Setting ex postion size usd")
                        self.__set_ex_position_size_usd()
                        if self.ex_position_size_usd > 0:
                            info_logger.debug("We are in a position updating order info")
                            self.order.position_size_usd = self.ex_position_size_usd
                            self.__set_order_average_entry()
                        else:
                            info_logger.debug("we are not in a position updating order info")
                            self.order.position_size_usd = 0.0
                            self.order.average_entry = 0.0
                            self.order.equity = self.exchange.get_equity_of_asset(trading_in=self.exchange.trading_in)
                            self.order.possible_loss = 0.0

                        self.order.calculate_stop_loss(
                            bar_index=bar_index,
                            candles=self.exchange.candles_np,
                        )
                        self.order.calculate_increase_posotion(
                            # entry price is close of the last bar
                            entry_price=self.exchange.candles_np[-1, 3],
                        )
                        self.order.calculate_leverage()
                        self.order.calculate_take_profit()

                        # place the order
                        send_verify_error = False
                        info_logger.info("Placing Entry Order")
                        entry_order_id = self.entry_order(
                            asset_amount=self.order.entry_size_asset,
                            entry_price=self.order.entry_price,
                        )

                        info_logger.info(f"Submitted entry order -> [order_id={entry_order_id}]")
                        sleep(1)

                        # check if order fileld
                        info_logger.debug(f"Checking if entry order was filled")
                        if self.exchange.check_if_order_filled(
                            symbol=self.symbol,
                            order_id=entry_order_id,
                        ):
                            info_logger.info("Entry was filled")
                        else:
                            msg += f"entry_order_id {entry_order_id} "
                            send_verify_error = True
                            info_logger.warning(f"Couldn't verify entry order was filled {entry_order_id}")

                        # cancel other orders if in position
                        info_logger.info(f"checking if in position to cancel tp and sl")
                        self.__set_ex_position_size_asset()
                        if self.ex_position_size_asset > 0:
                            info_logger.info(f"We are in a pos and trying to cancle tp and sl")
                            if self.exchange.cancel_all_open_order_per_symbol(symbol=self.symbol):
                                info_logger.info(f"Canceled the orders")
                            else:
                                info_logger.warning("Wasn't able to verify that the tp and sl were canceled")

                        sleep(0.5)

                        # set the levergae
                        info_logger.info("Setting leverage")
                        if self.exchange.set_leverage_value(
                            symbol=self.symbol,
                            leverage=self.order.leverage,
                        ):
                            info_logger.info(f"Leverage Changed")
                        else:
                            info_logger.warning("Couldn't verify that leverage was set")
                            msg += f"leverage was set "
                            send_verify_error = True

                        info_logger.info(f"Submitting stop loss order")
                        sl_order_id = self.place_sl_order(
                            asset_amount=self.ex_position_size_asset,
                            trigger_price=self.order.sl_price,
                        )
                        info_logger.info(f"Submitted SL order -> [order_id={sl_order_id}]")

                        sleep(0.5)
                        info_logger.info(f"Submitting take profit order")
                        tp_order_id = self.place_tp_order(
                            asset_amount=self.ex_position_size_asset,
                            tp_price=self.order.tp_price,
                        )
                        info_logger.info(f"Submitted TP order -> [order_id={tp_order_id}]")

                        # sleep 1 second before checking to see if orders were placed
                        sleep(1)
                        info_logger.info(f"Checking if stop loss was placed")
                        if self.exchange.check_if_order_open(
                            symbol=self.symbol,
                            order_id=sl_order_id,
                        ):
                            info_logger.info(f"Stop loss was placed")
                        else:
                            info_logger.warning(f"Couldn't verify sl order was placed {sl_order_id} ")
                            msg += f"sl_order_id {sl_order_id} "
                            send_verify_error = True

                        info_logger.debug(f"Checking if tp was placed")
                        if self.exchange.check_if_order_open(
                            symbol=self.symbol,
                            order_id=tp_order_id,
                        ):
                            info_logger.info(f"take profit placed")
                        else:
                            info_logger.info(f"Couldn't verify tp order was filled {tp_order_id}")
                            msg += f"tp_order_id {tp_order_id}"
                            send_verify_error = True

                        if send_verify_error:
                            info_logger.info("Something wan't verified so rechecking all")
                            entry_placed = self.exchange.check_if_order_filled(
                                symbol=self.symbol,
                                order_id=entry_order_id,
                            )
                            leverage_changed = self.exchange.set_leverage_value(
                                symbol=self.symbol,
                                leverage=self.order.leverage,
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
                                logging.error(msg)
                                raise Exception(msg)
                            info_logger.info("All verified")

                        else:
                            self.__set_exchange_variables(
                                entry_order_id=entry_order_id,
                                sl_order_id=sl_order_id,
                                tp_order_id=tp_order_id,
                            )
                            message = self.__create_entry_successful_message()
                            entry_filename = self.__get_entry_plot_filename()
                            strategy_filename = self.strategy.get_strategy_plot_filename()
                            # self.email_sender.email_new_order(
                            #     message=message,
                            #     entry_filename=entry_filename,
                            #     strategy_filename=strategy_filename,
                            # )
                            info_logger.info("Entry placed on exchange")
                            trade_logger.info(f"{message}")

                    except RejectedOrder as e:
                        info_logger.warning(f"RejectedOrder -> {e.msg}")
                        pass
                    except Exception as e:
                        info_logger.error(f"Exception Entry -> {e}")
                        raise Exception(f"Exception Entry -> {e}")
                    self.__set_ex_position_size_asset()
                    if self.ex_position_size_asset > 0:
                        info_logger.info(f"We are in a position ... checking to move stop loss")
                        try:
                            self.order.check_move_stop_loss_to_be(
                                bar_index=bar_index,
                                candles=self.exchange.candles_np,
                            )
                            info_logger.info(f"Wont move sl to be")
                            self.__set_order_average_entry()
                            self.order.check_move_trailing_stop_loss(
                                bar_index=bar_index,
                                candles=self.exchange.candles_np,
                            )
                            info_logger.info(f"Wont trail stop loss")
                        except MoveStopLoss as result:
                            try:
                                info_logger.info(
                                    f"trying to move the stop loss from {self.order.sl_price} to {result.sl_price}"
                                )
                                if self.exchange.move_stop_order(
                                    symbol=self.symbol,
                                    order_id=sl_order_id,
                                    asset_amount=self.ex_position_size_asset,
                                    new_price=result.sl_price,
                                ):
                                    info_logger.info(f"Moved stop loss from {self.order.sl_price} to {result.sl_price}")
                                    self.order.update_stop_loss_live_trading(sl_price=result.sl_price)
                                else:
                                    info_logger.warning(f"Couldn't verify sl was moved {sl_order_id}")
                            except Exception as e:
                                info_logger.error(f"Exception MoveStopLoss -> {e}")
                                raise Exception(f"Exception MoveStopLoss -> {e}")
                            pass
                        except Exception as e:
                            info_logger.error(f"Exception checking MoveStopLoss -> {e}")
                            raise Exception(f"Exception checking MoveStopLoss -> {e}")
                elif latest_pnl != self.last_pnl:
                    info_logger.info(f"Got a new pnl {latest_pnl}")
                    self.email_sender.email_pnl(pnl=latest_pnl)
                    self.last_pnl = latest_pnl
                else:
                    pass
            except Exception as e:
                info_logger.error(f"Exception -> {e}")
                info_logger.error("Server stopped")
                self.email_error_msg(msg=f"Exception -> {e}")
                raise Exception(f"Exception -> {e}")
            sleep(self.get_sleep_time_to_next_bar())

    def get_sleep_time_to_next_bar(self):
        ms_to_next_candle = max(
            0,
            (self.exchange.last_fetched_ms_time + self.exchange.timeframe_in_ms * 2)
            - self.exchange.get_current_time_ms(),
        )
        td = str(timedelta(seconds=ms_to_next_candle / 1000)).split(":")
        info_logger.info(f"Will sleep for {td[0]} hrs {td[1]} mins and {td[2]} seconds till next bar\n")
        print(f"Will sleep for {td[0]} hrs {td[1]} mins and {td[2]} seconds till next bar\n")

        return int(ms_to_next_candle / 1000)

    def email_error_msg(self, msg):
        info_logger.debug(f"")
        self.email_sender.email_error_msg(msg=msg)

    def __set_ex_position_size_asset(self):
        info_logger.debug(f"Setting position size asset")
        self.ex_position_size_asset = float(self.get_position_info()["size"])

    def __set_ex_position_size_usd(self):
        info_logger.debug(f"Setting position size usd")
        self.ex_position_size_usd = float(self.get_position_info()["positionValue"])

    def __set_order_average_entry(self):
        info_logger.debug(f"Setting average entry")
        self.order.average_entry = float(self.get_position_info()["entryPrice"])

    def __set_exchange_variables(self, entry_order_id, sl_order_id, tp_order_id):
        info_logger.debug(f"setting all exchange vars")
        pos_info = self.get_position_info()
        entry_info = self.exchange.get_filled_orders_by_order_id(symbol=self.symbol, order_id=entry_order_id)
        tp_info = self.exchange.get_open_order_by_order_id(symbol=self.symbol, order_id=tp_order_id)
        sl_info = self.exchange.get_open_order_by_order_id(symbol=self.symbol, order_id=sl_order_id)

        self.ex_position_size_asset = float(pos_info.get("size"))
        self.ex_position_size_usd = float(pos_info.get("positionValue"))
        self.ex_average_entry = float(pos_info.get("entryPrice"))
        self.ex_entry_price = float(entry_info.get("execPrice"))
        self.ex_entry_size_asset = float(entry_info.get("execQty"))
        self.ex_entry_size_usd = float(entry_info.get("execValue"))
        self.ex_leverage = float(pos_info.get("leverage"))
        self.ex_liq_price = float(pos_info.get("liqPrice"))
        self.ex_liq_pct = self.get_liq_pct(price=self.ex_liq_price, average_entry=self.ex_average_entry)
        self.ex_tp_price = float(tp_info.get("price"))
        self.ex_tp_pct = self.get_tp_pct(price=self.ex_tp_price, average_entry=self.ex_average_entry)
        self.ex_sl_price = float(sl_info.get("triggerPrice"))
        self.ex_sl_pct = self.get_sl_pct(price=self.ex_sl_price, average_entry=self.ex_average_entry)
        coin_size = self.ex_position_size_asset
        pnl = coin_size * (self.ex_sl_price - self.ex_average_entry)
        fee_open = coin_size * self.ex_average_entry * self.exchange.exchange_settings.market_fee_pct  # math checked
        fee_close = coin_size * self.ex_sl_price * self.exchange.exchange_settings.market_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.ex_possible_loss = round(-(pnl - self.fees_paid), 4)

    def __get_pct_dif_above_average_entry(self, price, average_entry):
        info_logger.debug(f"getting pct")
        return round(((price - average_entry) / average_entry) * 100, 2)

    def __get_pct_dif_below_average_entry(self, price, average_entry):
        info_logger.debug(f"getting pct")
        return round(((average_entry - price) / average_entry) * 100, 2)

    def __create_entry_successful_message(self):
        info_logger.debug(f"Creating message")
        message = f"An order was placed successfully\n\
[ex_candle_closing_price={self.exchange.candles_np[-1,3]}]\n\
[entry_price={self.order.entry_price}]\n\
[ex_entry_price={self.ex_entry_price}]\n\n\
[average_entry={self.order.average_entry}]\n\
[ex_average_entry={self.ex_average_entry}]\n\n\
[position_size_usd={self.order.position_size_usd}]\n\
[ex_position_size_usd={self.ex_position_size_usd}]\n\n\
[entry_size_usd={self.order.entry_size_usd}]\n\
[ex_entry_size_usd={self.ex_entry_size_usd}]\n\n\
[leverage={self.order.leverage}]\n\
[ex_leverage={self.ex_leverage}]\n\n\
[liq price={self.order.liq_price}]\n\
[ex_liq price={self.ex_liq_price}]\n\n\
[candle low={self.exchange.candles_np[-1,2]}]\n\
[stop_loss_price={self.order.sl_price}]\n\
[ex_stop_loss_price={self.ex_sl_price}]\n\n\
[take_profit_price={self.order.tp_price}]\n\
[ex_take_profit_price={self.ex_tp_price}]\n\n\
[possible loss={self.order.possible_loss}]\n\
[ex_possible loss={self.ex_possible_loss}]\n\n"
        return message

    def __get_entry_plot_filename(self):
        info_logger.debug("Getting entry plot file")
        last_20 = self.exchange.candles_df[-20:]
        graph_entry = [last_20.index[-1]]
        fig = go.Figure()
        fig.add_candlestick(
            x=last_20.index,
            open=last_20.open,
            high=last_20.high,
            low=last_20.low,
            close=last_20.close,
            name="Exchange order",
        )
        # entry
        fig.add_scatter(
            x=graph_entry,
            y=[self.order.entry_price],
            mode="markers",
            marker=dict(size=10, color="LightSeaGreen"),
            name=f"Entry",
        )
        # average entry
        fig.add_scatter(
            x=graph_entry,
            y=[self.ex_average_entry],
            mode="markers",
            marker=dict(size=10, color="purple", symbol='arrow-up'),
            name=f"Entry",
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
            f'entry_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.png',
        )
        fig.write_image(entry_filename)
        return entry_filename
