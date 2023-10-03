import logging
from time import sleep
from uuid import uuid4
from quantfreedom.email_sender import EmailSender
from quantfreedom.enums import LongOrShortType, MoveStopLoss, OrderPlacementType, RejectedOrderError

from quantfreedom.exchanges.base.exchange import Exchange
from quantfreedom.order_handler.order_handler import Order
from quantfreedom.strategies.strategy import Strategy


class LiveTrading:
    def __init__(
        self,
        exchange: Exchange,
        candles_to_dl: int,
        strategy: Strategy,
        order: Order,
        entry_order_type: OrderPlacementType,
        tp_order_type: OrderPlacementType,
        email_sender: EmailSender,
    ):
        self.exchange = exchange
        self.candles_to_dl = candles_to_dl
        self.strategy = strategy
        self.order = order
        self.email_sender = email_sender
        self.send_error_msg = self.email_error_msg
        self.send_plot_graph = self.send_entry_email
        self.__get_plot_file = self.__get_plot_fig_filename

        if self.exchange.long_or_short == LongOrShortType.Long:
            self.place_sl_order = self.exchange.create_long_sl_order
            if entry_order_type == OrderPlacementType.Market:
                self.check_entry_order = self.exchange.check_if_order_filled
                self.entry_order = self.exchange.create_long_entry_market_order
            else:
                self.check_entry_order = self.exchange.check_if_order_active
                self.entry_order = self.exchange.create_long_entry_limit_order

            if tp_order_type == OrderPlacementType.Market:
                self.place_tp_order = self.exchange.create_long_tp_market_order
            else:
                self.place_tp_order = self.exchange.create_long_tp_limit_order

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

        sleep(self.get_time_to_next_bar_seconds())
        while True:
            try:
                price_data = self.exchange.get_and_set_candles_df()[["open", "high", "low", "close"]].values

                # bar_index bar index is always the last bar ... so if we have 200 candles we are at index 200
                bar_index = price_data.shape()[0]
                msg = ""

                self.strategy.set_indicator_live_trading(self.exchange.candles_df)
                if self.strategy.evaluate():
                    try:
                        try:
                            if self.exchange.position_size_asset > 0:
                                self.exchange.in_position = True
                                self.order.position_size_usd = round(
                                    self.exchange.position_size_asset * self.exchange.average_entry, 4
                                )
                                self.order.average_entry = self.exchange.average_entry
                            else:
                                self.exchange.in_position = False
                                self.order.position_size_usd = 0.0
                                self.order.average_entry = 0.0
                            self.order.calculate_stop_loss(
                                bar_index=bar_index,
                                price_data=price_data,
                            )
                            self.order.calculate_increase_posotion(
                                # entry price is close of the last bar
                                entry_price=price_data[-1, 3],
                            )
                            self.order.calculate_leverage()
                            self.order.calculate_take_profit()
                            entry_size_asset = round(self.order.entry_size_usd / self.order.entry_price, 3)
                            entry_order_id = self.place_entry_order(
                                asset_amount=entry_size_asset,
                                entry_price=self.order.entry_price,
                            )

                            logging.info(f"Submitted entry order -> [order_id={entry_order_id}]")
                            sleep(0.2)

                            verify_entry_order = self.check_entry_order(order_id=entry_order_id)
                            if not verify_entry_order:
                                msg += f"Couldn't verify entry order was filled {entry_order_id} "
                                send_verify_error = True

                            if self.exchange.in_position:
                                if not self.cancel_tp_and_sl(tp_order_id=tp_order_id, sl_order_id=sl_order_id):
                                    logging.warning("Wasn't able to verify that the tp and sl were canceled")

                            sl_order_id = self.place_sl_order(
                                asset_amount=self.exchange.position_size_asset,
                                trigger_price=self.order.sl_price,
                            )
                            logging.info(f"Submitted SL order -> [order_id={sl_order_id}]")

                            tp_order_id = self.place_tp_order(
                                asset_amount=self.exchange.position_size_asset,
                                tp_price=self.order.tp_price,
                            )
                            logging.info(f"Submitted TP order -> [order_id={tp_order_id}]")
                            sleep(1)

                            verify_sl_order = self.exchange.check_if_order_active(order_id=sl_order_id)
                            if not verify_sl_order:
                                msg += f"Couldn't verify sl order was filled {sl_order_id} "
                                send_verify_error = True

                            verify_tp_order = self.exchange.check_if_order_active(order_id=tp_order_id)
                            if not verify_tp_order:
                                msg += f"Couldn't verify tp order was filled {tp_order_id}"
                                send_verify_error = True

                            if send_verify_error:
                                logging.error(msg)
                                self.send_error_msg(msg=msg)
                            else:
                                message = '\
            An order was placed successfully\
            \
            User data ->        [equity={entry_data_gathered.no_position_equity}]\n\
                                [average_entry={entry_data_gathered.average_entry}]\n\
                                [position_size={entry_data_gathered.position_size}]\n\
                                [take_profit_price={entry_data_gathered.take_profit_price}]\n\
                                [stop_loss_price={entry_data_gathered.stop_loss_price}]\n\
                                [entry_size_value={entry_data_gathered.entry_size_value}]\n\
                                [entry_size={entry_data_gathered.entry_size}]\n\
                                [candle_closing_price={entry_data_gathered.candle_closing_price}]\n\
                                [tpl={entry_data_gathered.tpl}]\n\
                                [leverage={entry_data_gathered.leverage}]\n\n\
                            \
            Exchange info ->    [average_entry={self.order_execution_strategy.average_entry}]\n\
                                [position_size={self.order_execution_strategy.position_size}]\n\
                                [position_size_usd={self.order_execution_strategy.position_size_usd}]\n\
                                [take_profit_price={self.order_execution_strategy.tp_price}]\n\
                                [take_profit_percent={self.order_execution_strategy.tp_pct}]\n\
                                [stop_loss_price={self.order_execution_strategy.sl_price}]\n\
                                [stop_loss_percent={self.order_execution_strategy.sl_pct}]\n\
                                [entry_size_value={self.order_execution_strategy.entry_size_value}]\n\
                                [entry_size={self.order_execution_strategy.entry_size}]\n\
                                [position_tpl={self.order_execution_strategy.tpl}]\n\
                                [leverage={self.order_execution_strategy.leverage}]\n\n\
                                [liq_price={self.order_execution_strategy.liq_price}]\n\n"'
                                logging.info()
                                pass

                        except RejectedOrderError as e:
                            pass

                        if self.exchange.in_position:
                            try:
                                self.order.check_move_stop_loss_to_be(bar_index=bar_index, price_data=price_data)
                                self.order.check_move_trailing_stop_loss(bar_index=bar_index, price_data=price_data)
                            except RejectedOrderError as e:
                                pass
                            except MoveStopLoss as result:
                                self.order.move_stop_loss_live_trading(sl_price=result.sl_price)
                                try:
                                    self.exchange.adjust_order(new_price=self.order.sl_price)
                                    ##############
                                    # TODO log that we moved the stop loss
                                    #################
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
                raise Exception
            sleep(self.get_time_to_next_bar_seconds())

    def get_time_to_next_bar_seconds(self):
        ms_to_next_candle = max(
            0,
            (self.exchange.last_fetched_ms_time + self.exchange.timeframe_in_ms * 2)
            - self.exchange.get_ms_current_time(),
        )

        return int(ms_to_next_candle / 1000)

    def place_entry_order(self, qty, orderLinkId, entry_price):
        return self.entry_order(
            qty=qty,
            orderLinkId=orderLinkId,
            price=entry_price,
        )

    def cancel_tp_and_sl(self, tp_order_id, sl_order_id):
        tp_canceled = False
        sl_canceled = False
        if self.exchange.check_if_order_active(order_id=tp_order_id):
            self.exchange.cancel_order(order_id=tp_order_id)
            tp_canceled = True
        if self.exchange.check_if_order_active(order_id=sl_order_id):
            self.exchange.cancel_order(order_id=sl_order_id)
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

    def __get_plot_fig_filename(self, entry_price, sl_price, tp_price, liq_price):
        return self.strategy.return_plot_image(
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp_price,
            liq_price=liq_price,
        )
