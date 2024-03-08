import os
import numpy as np
import plotly.graph_objects as go
import pandas as pd

from time import sleep
from datetime import datetime, timedelta
from logging import getLogger

from quantfreedom.email_sender import EmailSender
from quantfreedom.exchanges.exchange import Exchange
from quantfreedom.order_handler.order import OrderHandler
from quantfreedom.strategies.strategy import Strategy
from quantfreedom.enums import (
    CandleBodyType,
    OrderStatus,
    PositionModeType,
    RejectedOrder,
)

logger = getLogger("info")
trade_logger = getLogger("trades")


class MufexLiveMode:
    def __init__(
        self,
        email_sender: EmailSender,
        entry_order_type: str,
        exchange: Exchange,
        order: OrderHandler,
        strategy: Strategy,
        symbol: str,
        trading_with: str,
        tp_order_type: str,
    ):
        self.order = order
        self.exchange = exchange
        self.email_sender = email_sender
        self.symbol = symbol
        self.strategy = strategy
        self.trading_with = trading_with

        if self.exchange.position_mode == PositionModeType.HedgeMode:
            if strategy.long_short == "long":
                self.place_sl_order = exchange.create_long_hedge_mode_sl_order
                self.get_position_info = exchange.get_long_hedge_mode_position_info
                if entry_order_type == "market":
                    self.entry_order = exchange.create_long_hedge_mode_entry_market_order

                if tp_order_type == "limit":
                    self.place_tp_order = exchange.create_long_hedge_mode_tp_limit_order

        self.ex_position_size_asset = float(self.get_position_info(symbol=symbol).get("size"))
        self.order.equity = exchange.get_equity_of_asset(trading_with=trading_with)

    def run(
        self,
        candles_to_dl: int,
        timeframe: str,
    ):
        latest_pnl = 0

        logger.info(f"Starting live trading")
        print(f"Starting live trading")
        try:
            self.last_pnl = self.exchange.get_latest_pnl_result(symbol=self.symbol)
        except Exception as e:
            logger.error(f"get_latest_pnl_result {e}")
            pass
        entry_order_id = 0
        tp_order_id = 0
        sl_order_id = 0

        self.exchange.last_fetched_ms_time = int(
            self.exchange.get_candles(
                symbol=self.symbol,
                timeframe=timeframe,
            )[-1, CandleBodyType.Timestamp]
        )
        logger.info(f"Last Candle time {self.exchange.last_fetched_time_to_pd_datetime()}")

        sleep(self.get_sleep_time_to_next_bar())

        while True:
            try:
                logger.info("Getting Candles")
                print("Getting Candles")
                self.candles = self.exchange.get_candles(
                    symbol=self.symbol,
                    timeframe=timeframe,
                    candles_to_dl=candles_to_dl,
                )
                num_candles = self.candles.shape[0]
                print("got candles")

                # bar_index bar index is always the last bar ... so if we have 200 candles we are at index 199
                bar_index = num_candles - 1
                msg = "Couldn't verify that the following orders were placed "

                logger.debug("Setting indicator")
                try:
                    latest_pnl = self.exchange.get_latest_pnl_result(symbol=self.symbol)
                except Exception as e:
                    logger.error(f"get_latest_pnl_result {e}")
                logger.info("Evaluating Strat")
                if self.strategy.live_evaluate(candles=self.candles):
                    try:
                        logger.debug("Setting ex postion size usd")
                        self.__set_ex_position_size_usd()
                        if self.ex_position_size_usd > 0:
                            logger.debug("We are in a position updating order info")
                            self.order.position_size_usd = self.ex_position_size_usd
                            self.__set_order_average_entry()
                        else:
                            logger.debug("we are not in a position updating order info")
                            self.order.position_size_usd = 0.0
                            self.order.position_size_asset = 0.0
                            self.order.average_entry = 0.0
                            self.order.equity = self.exchange.get_equity_of_asset(trading_with=self.trading_with)
                            self.order.available_balance = self.order.equity
                            self.order.possible_loss = 0.0
                            self.order.cash_used = 0.0
                            self.order.cach_borrowed = 0.0

                        logger.debug("calculate_stop_loss")
                        sl_price = self.order.calculate_stop_loss(
                            bar_index=bar_index,
                            candles=self.candles,
                        )

                        logger.debug("calculate_increase_position")
                        (
                            average_entry,
                            entry_price,
                            entry_size_asset,
                            entry_size_usd,
                            position_size_asset,
                            position_size_usd,
                            possible_loss,
                            total_trades,
                            sl_pct,
                        ) = self.order.calculate_increase_position(
                            average_entry=self.order.average_entry,
                            entry_price=self.candles[bar_index, CandleBodyType.Close],
                            equity=self.order.equity,
                            position_size_asset=self.order.position_size_asset,
                            position_size_usd=self.order.position_size_usd,
                            possible_loss=self.order.possible_loss,
                            sl_price=sl_price,
                            total_trades=self.order.total_trades,
                        )

                        logger.debug("calculate_leverage")
                        (
                            available_balance,
                            cash_borrowed,
                            cash_used,
                            leverage,
                            liq_price,
                        ) = self.order.calculate_leverage(
                            available_balance=self.order.available_balance,
                            average_entry=average_entry,
                            cash_borrowed=self.order.cash_borrowed,
                            cash_used=self.order.cash_used,
                            position_size_usd=position_size_usd,
                            position_size_asset=position_size_asset,
                            sl_price=sl_price,
                        )

                        logger.debug("calculate_take_profit")
                        (
                            can_move_sl_to_be,
                            tp_price,
                            tp_pct,
                        ) = self.order.calculate_take_profit(
                            average_entry=average_entry,
                            position_size_usd=position_size_usd,
                            possible_loss=possible_loss,
                        )
                        logger.debug("filling order result")
                        self.order.fill_order_result(
                            available_balance=available_balance,
                            average_entry=average_entry,
                            can_move_sl_to_be=can_move_sl_to_be,
                            cash_borrowed=cash_borrowed,
                            cash_used=cash_used,
                            entry_price=entry_price,
                            entry_size_asset=entry_size_asset,
                            entry_size_usd=entry_size_usd,
                            equity=self.order.equity,
                            exit_price=np.nan,
                            fees_paid=np.nan,
                            leverage=leverage,
                            liq_price=liq_price,
                            order_status=OrderStatus.EntryFilled,
                            position_size_asset=position_size_asset,
                            position_size_usd=position_size_usd,
                            possible_loss=possible_loss,
                            realized_pnl=np.nan,
                            sl_pct=sl_pct,
                            sl_price=sl_price,
                            total_trades=total_trades,
                            tp_pct=tp_pct,
                            tp_price=tp_price,
                        )
                        logger.info("We are in a position and filled the result")

                        # place the order
                        send_verify_error = False
                        logger.info("Placing Entry Order")
                        entry_order_id = self.entry_order(
                            asset_size=self.order.entry_size_asset,
                            symbol=self.symbol,
                        )

                        logger.info(f"Submitted entry order -> [order_id={entry_order_id}]")
                        sleep(1)

                        # check if order fileld
                        logger.debug(f"Checking if entry order was filled")
                        if self.exchange.check_if_order_filled(
                            order_id=entry_order_id,
                            symbol=self.symbol,
                        ):
                            logger.info("Entry was filled")
                        else:
                            msg += f"entry_order_id {entry_order_id} "
                            send_verify_error = True
                            logger.warning(f"Couldn't verify entry order was filled {entry_order_id}")

                        # cancel other orders if in position
                        logger.info(f"checking if in position to cancel tp and sl")
                        self.__set_ex_position_size_asset()
                        if self.ex_position_size_asset > 0:
                            logger.info(f"We are in a pos and trying to cancel tp and sl")
                            if self.exchange.cancel_all_open_orders_per_symbol(symbol=self.symbol):
                                logger.info(f"Canceled the orders")
                            else:
                                logger.warning("Wasn't able to verify that the tp and sl were canceled")

                        sleep(1)

                        # set the levergae
                        logger.info("Setting leverage")
                        if self.exchange.set_leverage(
                            symbol=self.symbol,
                            leverage=self.order.leverage,
                        ):
                            logger.info(f"Leverage Changed")
                        else:
                            logger.warning("Couldn't verify that leverage was set")
                            msg += f"leverage was set "
                            send_verify_error = True

                        logger.info(f"Submitting stop loss order")
                        sl_order_id = self.place_sl_order(
                            asset_size=self.ex_position_size_asset,
                            symbol=self.symbol,
                            trigger_price=self.order.sl_price,
                        )
                        logger.info(f"Submitted SL order -> [order_id={sl_order_id}]")

                        sleep(1)
                        logger.info(f"Submitting take profit order")
                        tp_order_id = self.place_tp_order(
                            asset_size=self.ex_position_size_asset,
                            symbol=self.symbol,
                            tp_price=self.order.tp_price,
                        )
                        logger.info(f"Submitted TP order -> [order_id={tp_order_id}]")
                        # sleep 1 second before checking to see if orders were placed
                        sleep(1)
                        logger.info(f"Checking if stop loss was placed")
                        if self.exchange.check_if_order_open(
                            order_id=sl_order_id,
                            symbol=self.symbol,
                        ):
                            logger.info(f"Stop loss was placed")
                        else:
                            logger.warning(f"Couldn't verify sl order was placed {sl_order_id} ")
                            msg += f"sl_order_id {sl_order_id} "
                            send_verify_error = True

                        logger.debug(f"Checking if tp was placed")
                        if self.exchange.check_if_order_open(
                            order_id=tp_order_id,
                            symbol=self.symbol,
                        ):
                            logger.info(f"take profit placed")
                        else:
                            logger.info(f"Couldn't verify tp order was filled {tp_order_id}")
                            msg += f"tp_order_id {tp_order_id}"
                            send_verify_error = True

                        if send_verify_error:
                            logger.info("Something wan't verified so rechecking all")
                            entry_placed = self.exchange.check_if_order_filled(
                                symbol=self.symbol,
                                order_id=entry_order_id,
                            )
                            leverage_changed = self.exchange.set_leverage(
                                leverage=self.order.leverage,
                                symbol=self.symbol,
                            )
                            sl_placed = self.exchange.check_if_order_open(
                                order_id=sl_order_id,
                                symbol=self.symbol,
                            )
                            tp_placed = self.exchange.check_if_order_open(
                                order_id=tp_order_id,
                                symbol=self.symbol,
                            )
                            verify_list = [entry_placed, leverage_changed, sl_placed, tp_placed]
                            if not all(v == True for v in verify_list):
                                logger.error(msg)
                                raise Exception(msg)
                            logger.info("All verified")

                        else:
                            self.__set_exchange_variables(
                                entry_order_id=entry_order_id,
                                sl_order_id=sl_order_id,
                                tp_order_id=tp_order_id,
                            )
                            message = self.__create_entry_successful_message()
                            print('Placed a new Trade')
                            # entry_filename = self.__get_entry_plot_filename()
                            # strategy_filename = self.strategy.get_strategy_plot_filename(candles=self.candles)
                            # self.email_sender.email_new_order(
                            #     message=message,
                            #     entry_filename=entry_filename,
                            #     strategy_filename=strategy_filename,
                            # )
                            logger.info("Entry placed on exchange")
                            trade_logger.info(f"{message}")

                    except RejectedOrder as e:
                        pass
                    except Exception as e:
                        logger.error(f"Exception Entry -> {e}")
                        raise Exception(f"Exception Entry -> {e}")
                    self.__set_ex_position_size_asset()
                    if self.ex_position_size_asset > 0:
                        logger.info(f"We are in a position ... checking to move stop loss")
                        try:
                            current_candle = self.candles[bar_index, :]
                            logger.debug("Checking to move stop to break even")
                            sl_to_be_price, sl_to_be_pct = self.order.check_move_sl_to_be(current_candle=current_candle)
                            if sl_to_be_price:
                                if self.exchange.move_stop_order(
                                    symbol=self.symbol,
                                    order_id=sl_order_id,
                                    asset_size=self.ex_position_size_asset,
                                    new_price=sl_to_be_price,
                                ):
                                    logger.info(f"Moved stop loss from {self.order.sl_price} to {sl_to_be_price}")
                                    self.order.sl_price = sl_to_be_price
                                    self.order.sl_pct = sl_to_be_pct
                                else:
                                    logger.warning(f"Couldn't verify sl to be was moved {sl_order_id}")
                                    raise Exception(f"Exception Move sl to be -> {e}")

                            logger.debug("Checking to move trailing stop loss")
                            tsl_price, tsl_pct = self.order.check_move_tsl(current_candle=current_candle)
                            if tsl_price:
                                if self.exchange.move_stop_order(
                                    symbol=self.symbol,
                                    order_id=sl_order_id,
                                    asset_size=self.ex_position_size_asset,
                                    new_price=tsl_price,
                                ):
                                    logger.info(f"Moved stop loss from {self.order.sl_price} to {tsl_price}")
                                    self.order.sl_price = tsl_price
                                    self.order.sl_price = tsl_pct
                                else:
                                    logger.warning(f"Couldn't verify tsl was moved {sl_order_id}")
                                    raise Exception(f"Exception Move TSL -> {e}")

                        except Exception as e:
                            logger.error(f"Exception checking MoveStopLoss -> {e}")
                            raise Exception(f"Exception checking MoveStopLoss -> {e}")
                elif latest_pnl != self.last_pnl:
                    print(f"Got a new pnl {latest_pnl}")
                    logger.info(f"Got a new pnl {latest_pnl}")
                    # self.email_sender.email_pnl(pnl=latest_pnl)
                    self.last_pnl = latest_pnl
                else:
                    pass
            except Exception as e:
                logger.error(f"Exception -> {e}")
                # self.email_sender.email_error_msg(msg=f"Exception -> {e}")
                raise Exception(f"Exception -> {e}")
            sleep(self.get_sleep_time_to_next_bar())

    def get_sleep_time_to_next_bar(self):
        ms_to_next_candle = max(
            0,
            (self.exchange.last_fetched_ms_time + self.exchange.timeframe_in_ms * 2)
            - self.exchange.get_current_time_ms(),
        )
        td = str(timedelta(seconds=ms_to_next_candle / 1000)).split(":")
        logger.info(f"Will sleep for {td[0]} hrs {td[1]} mins and {td[2]} seconds till next bar\n")
        print(f"Will sleep for {td[0]} hrs {td[1]} mins and {td[2]} seconds till next bar\n")

        return int(ms_to_next_candle / 1000)

    def __set_ex_position_size_asset(self):
        logger.debug(f"Setting position size asset")
        self.ex_position_size_asset = float(self.get_position_info(symbol=self.symbol)["size"])

    def __set_ex_position_size_usd(self):
        logger.debug(f"Setting position size usd")
        pos_val = self.get_position_info(symbol=self.symbol)["positionValue"]
        self.ex_position_size_usd = 0 if pos_val == "" else float(pos_val)

    def __set_order_average_entry(self):
        logger.debug(f"Setting average entry")
        self.order.average_entry = float(self.get_position_info(symbol=self.symbol)["entryPrice"])

    def __set_ex_possible_loss(self):
        logger.debug(f"setting all exchange vars")
        coin_size = self.ex_position_size_asset
        pnl = coin_size * (self.ex_sl_price - self.ex_average_entry)
        fee_open = coin_size * self.ex_average_entry * self.exchange.exchange_settings.market_fee_pct  # math checked
        fee_close = coin_size * self.ex_sl_price * self.exchange.exchange_settings.market_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.ex_possible_loss = round(abs(pnl - self.fees_paid), 3)

    def __set_ex_possible_profit(self):
        logger.debug(f"setting all exchange vars")
        coin_size = self.ex_position_size_asset
        pnl = coin_size * (self.ex_tp_price - self.ex_average_entry)
        fee_open = coin_size * self.ex_average_entry * self.exchange.exchange_settings.market_fee_pct  # math checked
        fee_close = coin_size * self.ex_tp_price * self.exchange.exchange_settings.limit_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.ex_possible_profit = round(abs(pnl - self.fees_paid), 3)

    def __set_exchange_variables(self, entry_order_id, sl_order_id, tp_order_id):
        logger.debug(f"setting all exchange vars")
        pos_info = self.get_position_info(symbol=self.symbol)
        entry_info = self.exchange.get_filled_order_by_order_id(symbol=self.symbol, order_id=entry_order_id)
        tp_info = self.exchange.get_open_order_by_order_id(symbol=self.symbol, order_id=tp_order_id)
        sl_info = self.exchange.get_open_order_by_order_id(symbol=self.symbol, order_id=sl_order_id)

        self.ex_position_size_asset = float(pos_info.get("size"))
        self.ex_position_size_usd = float(pos_info.get("positionValue"))
        self.ex_average_entry = float(pos_info.get("entryPrice"))
        self.avg_entry_slippage = self.__get_pct_difference(self.order.average_entry, self.ex_average_entry)
        self.ex_entry_price = float(entry_info.get("execPrice"))
        self.entry_slippage = self.__get_pct_difference(self.order.entry_price, self.ex_entry_price)
        self.ex_entry_size_asset = float(entry_info.get("orderQty"))
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
        logger.debug(f"getting pct difference")
        return round(abs((starting_num - diff_num) / starting_num) * 100, 3)

    def __create_entry_successful_message(self):
        logger.debug(f"Creating message")
        self.__set_ex_possible_loss()
        self.__set_ex_possible_profit()

        message = f"An order was placed successfully\
            \n[ex_candle_closing_price={self.candles[-1,CandleBodyType.Close]}]\
            \n[entry_price={self.order.entry_price}]\
            \n[ex_entry_price={self.ex_entry_price}]\
            \n[Entry slippage={self.entry_slippage}]\
            \n[average_entry={self.order.average_entry}]\
            \n[ex_average_entry={self.ex_average_entry}]\
            \n[Average Entry slippage={self.avg_entry_slippage}]\
            \n[position_size_usd={self.order.position_size_usd}]\
            \n[ex_position_size_usd={self.ex_position_size_usd}]\
            \n[entry_size_usd={self.order.entry_size_usd}]\
            \n[ex_entry_size_usd={self.ex_entry_size_usd}]\
            \n[leverage={self.order.leverage}]\
            \n[ex_leverage={self.ex_leverage}]\
            \n[liq price={self.order.liq_price}]\
            \n[ex_liq price={self.ex_liq_price}]\
            \n[ex_liq_pct={self.ex_liq_pct}]\
            \n[candle low={self.candles[-1,CandleBodyType.Low]}]\
            \n[stop_loss_price={self.order.sl_price}]\
            \n[ex_stop_loss_price={self.ex_sl_price}]\
            \n[sl_pct={round(self.order.sl_pct * 100, 3)}]\
            \n[ex_sl_pct={self.ex_sl_pct}]\
            \n[take_profit_price={self.order.tp_price}]\
            \n[ex_take_profit_price={self.ex_tp_price}]\
            \n[tp_pct={round(self.order.tp_pct * 100, 3)}]\
            \n[ex_tp_pct={self.ex_tp_pct}]\
            \n[possible loss={self.order.possible_loss}]\
            \n[ex_possible loss={self.ex_possible_loss}]\
            \n[ex_possible profit={self.ex_possible_profit}]"
        return message

    # def __get_entry_plot_filename(self):
    #     logger.debug("Getting entry plot file")
    #     latest_candles = self.candles[-50:]
    #     latest_candles_datetimes = pd.to_datetime(latest_candles[:, CandleBodyType.Timestamp], unit="ms")
    #     graph_entry = [latest_candles_datetimes[-1]]
    #     fig = go.Figure()
    #     fig.add_candlestick(
    #         x=latest_candles_datetimes,
    #         open=latest_candles[:, CandleBodyType.Open],
    #         high=latest_candles[:, CandleBodyType.High],
    #         low=latest_candles[:, CandleBodyType.Low],
    #         close=latest_candles[:, CandleBodyType.Close],
    #         name="Exchange order",
    #     )
    #     # entry
    #     fig.add_scatter(
    #         x=graph_entry,
    #         y=[self.order.entry_price],
    #         mode="markers",
    #         marker=dict(size=10, color="LightSeaGreen"),
    #         name=f"Entry",
    #     )
    #     # average entry
    #     fig.add_scatter(
    #         x=graph_entry,
    #         y=[self.ex_average_entry],
    #         mode="markers",
    #         marker=dict(size=10, color="purple", symbol="arrow-up"),
    #         name=f"Average Entry",
    #     )
    #     # take profit
    #     fig.add_scatter(
    #         x=graph_entry,
    #         y=[self.ex_tp_price],
    #         mode="markers",
    #         marker=dict(size=10, symbol="star", color="Green"),
    #         name=f"Take Profit",
    #     )
    #     # stop loss
    #     fig.add_scatter(
    #         x=graph_entry,
    #         y=[self.ex_sl_price],
    #         mode="markers",
    #         marker=dict(size=10, symbol="x", color="orange"),
    #         name=f"Stop Loss",
    #     )
    #     # liq price
    #     fig.add_scatter(
    #         x=graph_entry,
    #         y=[self.ex_liq_price],
    #         mode="markers",
    #         marker=dict(size=10, symbol="hexagram", color="red"),
    #         name=f"Liq Price",
    #     )
    #     fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    #     fig.show()
    #     entry_filename = os.path.join(
    #         self.strategy.log_folder,
    #         "logs",
    #         "images",
    #         f'entry_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.png',
    #     )
    #     fig.write_image(entry_filename)
    #     return entry_filename
