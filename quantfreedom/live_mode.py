import logging
from time import sleep
from uuid import uuid4
from quantfreedom.email_sender import EmailSender
from quantfreedom.enums import LongOrShortType, MoveStopLoss, OrderPlacementType, PositionModeType, RejectedOrderError

from quantfreedom.exchanges.base.live_exchange import LiveExchange
from quantfreedom.order_handler.order_handler import Order
from quantfreedom.strategies.strategy import Strategy


class LiveTrading:
    ex_position_size_asset = 0

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
        self.send_error_msg = self.email_error_msg
        self.send_plot_graph = self.send_entry_email
        self.__get_plot_file = self.__get_fig_filename

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

    def pass_function(self, **vargs):
        pass

    def run(self):
        entry_order_id = 0
        tp_order_id = 0
        sl_order_id = 0

        self.exchange.set_init_last_fetched_time()
        logging.info(f"Last Candle {self.exchange.last_fetched_time_to_pd_datetime()}")
        logging.info(
            f"Will sleep for {round(self.get_time_to_next_bar_seconds()/60,2)} minutes before getting first batch of candles"
        )
        print(
            f"Will sleep for {round(self.get_time_to_next_bar_seconds()/60,2)} minutes before getting first batch of candles"
        )

        sleep(self.get_time_to_next_bar_seconds())
        while True:
            try:
                print("Getting Candles")
                self.exchange.set_candles_df_and_np()

                # bar_index bar index is always the last bar ... so if we have 200 candles we are at index 200
                bar_index = self.exchange.candles_np.shape[0]
                msg = ""

                self.strategy.set_indicator_live_trading(self.exchange.candles_df)
                logging.info("Evaluating Strat")
                if self.strategy.evaluate():
                    logging.info("Maybe we place a trade")
                    try:
                        try:
                            if self.ex_position_size_asset > 0:
                                logging.info("if self.ex_position_size_asset > 0:")
                                self.ex_in_position = True
                                self.order.position_size_usd = self.ex_position_size_usd
                                self.order.average_entry = self.ex_average_entry
                                self.order.equity = self.exchange.get_equity_of_asset(
                                    trading_in=self.exchange.trading_in
                                )
                            else:
                                logging.info("else part of if self.ex_position_size_asset > 0:")
                                self.ex_in_position = False
                                self.order.position_size_usd = 0.0
                                self.order.average_entry = 0.0
                            logging.info("self.order.calculate_stop_loss")
                            self.order.calculate_stop_loss(
                                bar_index=bar_index,
                                price_data=self.exchange.candles_np,
                            )
                            logging.info("self.order.calculate_increase_posotion")
                            self.order.calculate_increase_posotion(
                                # entry price is close of the last bar
                                entry_price=self.exchange.candles_np[-1, 3],
                            )
                            logging.info("self.order.calculate_leverage")
                            self.order.calculate_leverage()
                            logging.info("self.order.calculate_take_profit")
                            self.order.calculate_take_profit()

                            # place the order
                            logging.info("entry_size_asset = round(self.order.entry_size_usd")
                            entry_size_asset = round(self.order.entry_size_usd / self.order.entry_price, 3)
                            send_verify_error = False
                            logging.info("entry_order_id = self.place_entry_order")
                            entry_order_id = self.place_entry_order(
                                asset_amount=entry_size_asset,
                                entry_price=self.order.entry_price,
                            )

                            logging.info(f"Submitted entry order -> [order_id={entry_order_id}]")
                            sleep(0.5)

                            # check if order fileld
                            logging.info(f"Checking if entry order was filled")
                            verify_entry_order = self.exchange.check_if_order_filled(
                                symbol=self.exchange.symbol,
                                order_id=entry_order_id,
                            )
                            if not verify_entry_order:
                                logging.info(f"Couldn't verify entry order was filled {entry_order_id} ")
                                msg += f"Couldn't verify entry order was filled {entry_order_id} "
                                send_verify_error = True
                            logging.info(f"entry order was filled")
                            # cancel other orders if in position
                            logging.info(f"checking if in position to cancel tp and sl")
                            if self.ex_in_position:
                                logging.info(f"we are in a pos and trying to cancle tp and sl")
                                if not self.cancel_tp_and_sl(
                                    tp_order_id=tp_order_id,
                                    sl_order_id=sl_order_id,
                                ):
                                    logging.warning("Wasn't able to verify that the tp and sl were canceled")
                            sleep(0.2)
                            # place stop loss order
                            self.__set_ex_position_size_asset()
                            logging.info(f"__set_ex_position_size_asset {self.ex_position_size_asset}")
                            logging.info(f"placing stop loss order")
                            sl_order_id = self.place_sl_order(
                                asset_amount=self.ex_position_size_asset,
                                trigger_price=self.order.sl_price,
                            )
                            logging.info(f"Submitted SL order -> [order_id={sl_order_id}]")
                            sleep(0.2)
                            logging.info(f"placing take profit order")
                            tp_order_id = self.place_tp_order(
                                asset_amount=self.ex_position_size_asset,
                                tp_price=round(self.order.tp_price, 1),  # TODO fix this later
                            )
                            logging.info(f"Submitted TP order -> [order_id={tp_order_id}]")

                            # sleep 1 second before checking to see if orders were placed
                            sleep(1)
                            verify_sl_order = self.exchange.check_if_order_open(
                                symbol=self.exchange.symbol,
                                order_id=sl_order_id,
                            )

                            # checking if tp and sl were placed
                            if not verify_sl_order:
                                msg += f"Couldn't verify sl order was filled {sl_order_id} "
                                send_verify_error = True

                            verify_tp_order = self.exchange.check_if_order_open(
                                symbol=self.exchange.symbol,
                                order_id=tp_order_id,
                            )
                            if not verify_tp_order:
                                msg += f"Couldn't verify tp order was filled {tp_order_id}"
                                send_verify_error = True

                            if send_verify_error:
                                logging.error(msg)
                                self.send_error_msg(msg=msg)
                            else:
                                message = self.__create_entry_successful_message(
                                    entry_order_id=entry_order_id,
                                    sl_order_id=sl_order_id,
                                    tp_order_id=tp_order_id,
                                )
                                fig_filename = self.__get_fig_filename(
                                    entry_price=self.ex_entry_price,
                                    sl_price=self.ex_sl_price,
                                    tp_price=self.ex_tp_price,
                                    liq_price=self.ex_liq_price,
                                )
                                self.email_sender.email_new_order(
                                    message=message,
                                    fig_filename=fig_filename,
                                )
                                logging.info(f"{message}")
                                pass

                        except RejectedOrderError as e:
                            pass

                        if self.ex_in_position:
                            try:
                                self.order.check_move_stop_loss_to_be(
                                    bar_index=bar_index,
                                    price_data=self.exchange.candles_np,
                                )
                                self.order.check_move_trailing_stop_loss(
                                    bar_index=bar_index,
                                    price_data=self.exchange.candles_np,
                                )
                            except RejectedOrderError as e:
                                pass
                            except MoveStopLoss as result:
                                try:
                                    self.exchange.move_open_order(
                                        symbol=self.exchange.symbol,
                                        order_id=sl_order_id,
                                        new_price=result.sl_price,
                                    )
                                    logging.info(f"Moved the stop loss from {self.order.sl_price} to {result.sl_price}")
                                    self.order.update_stop_loss_live_trading(sl_price=result.sl_price)
                                except KeyError as e:
                                    logging.error(f"Something wrong with move stop loss -> {e}")
                                    raise KeyError

                    except Exception as e:
                        logging.error(f"Something is wrong in the order creation part of live mode -> {e}")
                        raise Exception
                else:
                    logging.info("No entry ... waiting to get next bar")
            except Exception as e:
                logging.error(f"Something is wrong in the run part of live mode -> {e}")
                raise Exception(f"Something is wrong in the run part of live mode -> {e}")
            logging.info(
                f"Will sleep for {round(self.get_time_to_next_bar_seconds()/60,2)} minutes before getting first batch of candles"
            )
            print(
                f"Will sleep for {round(self.get_time_to_next_bar_seconds()/60,2)} minutes before getting first batch of candles"
            )
            sleep(self.get_time_to_next_bar_seconds())

    def get_time_to_next_bar_seconds(self):
        ms_to_next_candle = max(
            0,
            (self.exchange.last_fetched_ms_time + self.exchange.timeframe_in_ms * 2)
            - self.exchange.get_current_time_ms(),
        )

        return int(ms_to_next_candle / 1000)

    def place_entry_order(self, asset_amount, entry_price):
        return self.entry_order(
            asset_amount=asset_amount,
            price=entry_price,
        )

    def cancel_tp_and_sl(self, tp_order_id, sl_order_id):
        tp_canceled = False
        sl_canceled = False
        if self.exchange.get_open_orders_by_order_id(symbol=self.exchange.symbol, order_id=tp_order_id):
            self.exchange.cancel_open_order(symbol=self.exchange.symbol, order_id=tp_order_id)
            tp_canceled = True
        if self.exchange.get_open_orders_by_order_id(symbol=self.exchange.symbol, order_id=sl_order_id):
            self.exchange.cancel_open_order(symbol=self.exchange.symbol, order_id=sl_order_id)
            sl_canceled = True
        if tp_canceled and sl_canceled:
            return True
        else:
            return False

    def email_error_msg(self, msg):
        self.email_sender.email_error_msg(msg=msg)

    def send_entry_email(self, entry_price, sl_price, tp_price, liq_price, body):
        fig_filename = self.__get_plot_file(
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp_price,
            liq_price=liq_price,
        )
        self.email_sender.email_new_order(body=body, fig_filename=fig_filename)

    def __get_fig_filename(self, entry_price, sl_price, tp_price, liq_price):
        return self.strategy.return_plot_image(
            price_data=self.exchange.candles_df,
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp_price,
            liq_price=liq_price,
        )

    def __set_ex_position_size_asset(self):
        self.ex_position_size_asset = float(self.get_position_info().get("size"))

    def __set_exchange_variables(self, entry_order_id, sl_order_id, tp_order_id):
        pos_info = self.get_position_info()
        entry_info = self.exchange.get_filled_orders_by_order_id(symbol=self.exchange.symbol, order_id=entry_order_id)
        tp_info = self.exchange.get_open_orders_by_order_id(symbol=self.exchange.symbol, order_id=tp_order_id)
        sl_info = self.exchange.get_open_orders_by_order_id(symbol=self.exchange.symbol, order_id=sl_order_id)

        self.ex_position_size_asset = float(pos_info.get("size"))
        self.ex_position_size_usd = float(pos_info.get("positionValue"))
        self.ex_average_entry = float(pos_info.get("entryPrice"))
        self.ex_entry_price = round(float(entry_info.get("execQty")) / float(entry_info.get("cumExecValue")), 2)
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
        self.ex_possible_loss = pnl - self.fees_paid

    def __get_pct_dif_above_average_entry(self, price, average_entry):
        return (price - average_entry) / average_entry

    def __get_pct_dif_below_average_entry(self, price, average_entry):
        return (average_entry - price) / average_entry

    def __create_entry_successful_message(self, entry_order_id, sl_order_id, tp_order_id):
        self.__set_exchange_variables(
            entry_order_id=entry_order_id,
            sl_order_id=sl_order_id,
            tp_order_id=tp_order_id,
        )
        return f"\
            An order was placed successfully\
            \
            User data ->        [average_entry={self.order.average_entry}]\n\
                                [position_size_usd={self.order.position_size_usd}]\n\
                                [entry_price={self.order.entry_price}]\n\
                                [entry_size_usd={self.order.entry_size_usd}]\n\
                                [leverage={self.order.leverage}]\n\n\
                                [liq price={self.order.liq_price}]\n\n\
                                [take_profit_price={self.order.tp_price}]\n\
                                [stop_loss_price={self.order.sl_price}]\n\
                                [possible loss={self.order.possible_loss}]\n\
                            \
            Exchange info ->    [candle_closing_price={self.exchange.candles_np[-1,3]}]\n\
                                [average_entry={self.order.average_entry}]\n\
                                [entry_price={self.order.entry_price}]\n\
                                [position_size_usd={self.order.position_size_usd}]\n\
                                [leverage={self.order.leverage}]\n\n\
                                [liq price={self.order.liq_price}]\n\n\
                                [entry_size_usd={self.order.entry_size_usd}]\n\
                                [take_profit_price={self.order.tp_price}]\n\
                                [stop_loss_price={self.order.sl_price}]\n\
                                [possible loss={self.ex_possible_loss}]\n"
