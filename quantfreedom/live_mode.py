import logging
from time import sleep
from uuid import uuid4
from quantfreedom.email_sender import EmailSender
from quantfreedom.enums import LongOrShortType, MoveStopLoss, OrderPlacementType, PositionModeType, RejectedOrderError
from quantfreedom.exchanges.live_exchange import LiveExchange
from quantfreedom.order_handler.order_handler import Order
from quantfreedom.strategies.strategy import Strategy
from datetime import datetime


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
        self.send_error_msg = self.email_error_msg
        self.send_plot_graph = self.send_entry_email
        self.__get_plot_file = self.__get_fig_filename

        # logging stuff
        self.info_logger = logging.getLogger("info")
        self.warning_logger = logging.getLogger("warnings")
        self.error_logger = logging.getLogger("errors")
        self.debug_logger = logging.getLogger("debug")
        self.entry_logger = logging.getLogger("entry")
        self.moved_sl_logger = logging.getLogger("moved_sl")

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
        entry_order_id = 0
        tp_order_id = 0
        sl_order_id = 0

        self.exchange.set_init_last_fetched_time()
        self.info_logger.info(f"Last Candle {self.exchange.last_fetched_time_to_pd_datetime()}")
        self.info_logger.info(
            f"Will sleep for {datetime.fromtimestamp(self.get_time_to_next_bar_seconds()).strftime('%M mins and %S seconds')} before getting first batch of candles"
        )
        print(
            f"Will sleep for {datetime.fromtimestamp(self.get_time_to_next_bar_seconds()).strftime('%M mins and %S seconds')} before getting first batch of candles"
        )

        sleep(self.get_time_to_next_bar_seconds())
        while True:
            try:
                print("Getting Candles")
                start_time = self.exchange.get_current_time_seconds()
                self.exchange.set_candles_df_and_np()
                time_it_took_in_seconds = self.exchange.get_current_time_seconds() - start_time
                self.info_logger.info(f"It took {time_it_took_in_seconds} seconds to download the candles")
                self.info_logger.info(f"Got a total of {self.exchange.candles_df.shape[0]} candles")

                # bar_index bar index is always the last bar ... so if we have 200 candles we are at index 200
                bar_index = self.exchange.candles_np.shape[0] - 1
                msg = "Couldn't verify that the following orders were placed "

                self.strategy.set_indicator_live_trading(self.exchange.candles_df)
                self.info_logger.info("Evaluating Strat")
                if self.strategy.evaluate():
                    self.info_logger.info("Maybe we place a trade")
                    try:
                        try:
                            self.__set_ex_position_size_usd()
                            if self.ex_position_size_usd > 0:
                                self.info_logger.info("if self.ex_position_size_asset > 0:")
                                self.order.position_size_usd = self.ex_position_size_usd
                                self.order.average_entry = self.__get_position_average_entry()
                            else:
                                self.info_logger.info("else part of if self.ex_position_size_asset > 0:")
                                self.order.position_size_usd = 0.0
                                self.order.average_entry = 0.0
                                self.order.equity = self.exchange.get_equity_of_asset(
                                    trading_in=self.exchange.trading_in
                                )
                            self.info_logger.info("self.order.calculate_stop_loss")
                            self.order.calculate_stop_loss(
                                bar_index=bar_index,
                                price_data=self.exchange.candles_np,
                            )
                            self.info_logger.info("self.order.calculate_increase_posotion")
                            self.order.calculate_increase_posotion(
                                # entry price is close of the last bar
                                entry_price=self.exchange.candles_np[-1, 3],
                            )
                            self.info_logger.info("self.order.calculate_leverage")
                            self.order.calculate_leverage()
                            self.info_logger.info("self.order.calculate_take_profit")
                            self.order.calculate_take_profit()

                            # create variables
                            entry_size_asset = self.order.entry_size_usd / self.order.entry_price
                            entry_size_asset = self.order.round_size_by_tick_step(
                                user_num=entry_size_asset,
                                exchange_num=self.exchange.exchange_settings.asset_tick_step,
                            )

                            entry_price = self.order.round_size_by_tick_step(
                                user_num=self.order.entry_price,
                                exchange_num=self.exchange.exchange_settings.price_tick_step,
                            )
                            sl_price = self.order.round_size_by_tick_step(
                                user_num=self.order.sl_price,
                                exchange_num=self.exchange.exchange_settings.price_tick_step,
                            )
                            tp_price = self.order.round_size_by_tick_step(
                                user_num=self.order.tp_price,
                                exchange_num=self.exchange.exchange_settings.price_tick_step,
                            )

                            leverage = self.order.round_size_by_tick_step(
                                user_num=self.order.leverage,
                                exchange_num=self.exchange.exchange_settings.leverage_tick_step,
                            )

                            # place the order
                            self.info_logger.info("entry_size_asset = round(self.order.entry_size_usd")
                            send_verify_error = False
                            self.info_logger.info("entry_order_id = self.place_entry_order")
                            entry_order_id = self.place_entry_order(
                                asset_amount=entry_size_asset,
                                entry_price=entry_price,
                            )

                            self.info_logger.info(f"Submitted entry order -> [order_id={entry_order_id}]")
                            sleep(1)

                            # check if order fileld
                            self.info_logger.info(f"Checking if entry order was filled")
                            entry_placed = self.exchange.check_if_order_filled(
                                symbol=self.exchange.symbol,
                                order_id=entry_order_id,
                            )
                            if not entry_placed:
                                msg += f"entry_order_id {entry_order_id} "
                                send_verify_error = True
                                self.warning_logger.info(f"Couldn't verify entry order was filled {entry_order_id} ")

                            # cancel other orders if in position
                            self.info_logger.info(f"checking if in position to cancel tp and sl")
                            self.__set_ex_position_size_asset()
                            if self.ex_position_size_asset > 0:
                                self.info_logger.info(f"we are in a pos and trying to cancle tp and sl")
                                if not self.exchange.cancel_all_open_order_per_symbol(symbol=self.exchange.symbol):
                                    self.warning_logger.info("Wasn't able to verify that the tp and sl were canceled")

                            sleep(0.5)

                            # set the levergae
                            leverage_changed = self.exchange.set_leverage_value(
                                symbol=self.exchange.symbol,
                                leverage=leverage,
                            )
                            self.info_logger.info(f"if not leverage_changed")
                            # checking if tp and sl were placed
                            if not leverage_changed:
                                self.warning_logger.info("Couldn't verify that leverage was set")
                                msg += f"leverage was set "
                                send_verify_error = True
                            # place stop loss order

                            self.info_logger.info(f"__set_ex_position_size_asset {self.ex_position_size_asset}")

                            self.info_logger.info(f"placing stop loss order")
                            sl_order_id = self.place_sl_order(
                                asset_amount=self.ex_position_size_asset,
                                trigger_price=sl_price,
                            )
                            self.info_logger.info(f"Submitted SL order -> [order_id={sl_order_id}]")

                            sleep(0.5)
                            self.info_logger.info(f"placing take profit order")
                            tp_order_id = self.place_tp_order(
                                asset_amount=self.ex_position_size_asset,
                                tp_price=tp_price,
                            )
                            self.info_logger.info(f"Submitted TP order -> [order_id={tp_order_id}]")

                            # sleep 1 second before checking to see if orders were placed
                            sleep(1)
                            self.info_logger.info(f"self.exchange.check_if_order_open")
                            sl_placed = self.exchange.check_if_order_open(
                                symbol=self.exchange.symbol,
                                order_id=sl_order_id,
                            )
                            self.info_logger.info(f"if not sl_placed")
                            # checking if tp and sl were placed
                            if not sl_placed:
                                self.warning_logger.info(f"Couldn't verify sl order was filled {sl_order_id} ")
                                msg += f"sl_order_id {sl_order_id} "
                                send_verify_error = True

                            self.info_logger.info(f"tp_placed = self.exchange.check_if_order_open")
                            tp_placed = self.exchange.check_if_order_open(
                                symbol=self.exchange.symbol,
                                order_id=tp_order_id,
                            )
                            self.info_logger.info(f"if not tp_placed")
                            if not tp_placed:
                                self.warning_logger.info(f"Couldn't verify tp order was filled {tp_order_id}")
                                msg += f"tp_order_id {tp_order_id}"
                                send_verify_error = True

                            self.info_logger.info(f"if send_verify_error")
                            if send_verify_error:
                                entry_placed = self.exchange.check_if_order_filled(
                                    symbol=self.exchange.symbol,
                                    order_id=entry_order_id,
                                )
                                leverage_changed = self.exchange.set_leverage_value(
                                    symbol=self.exchange.symbol,
                                    leverage=leverage,
                                )
                                sl_placed = self.exchange.check_if_order_open(
                                    symbol=self.exchange.symbol,
                                    order_id=sl_order_id,
                                )
                                tp_placed = self.exchange.check_if_order_open(
                                    symbol=self.exchange.symbol,
                                    order_id=tp_order_id,
                                )
                                verify_list = [entry_placed, leverage_changed, sl_placed, tp_placed]
                                if all(v == True for v in verify_list):
                                    logging.error(msg)
                                    self.send_error_msg(msg=msg)
                                    break

                            else:
                                self.info_logger.info(f"message = self.__create_entry_successful_message")
                                # message = self.__create_entry_successful_message(
                                #     entry_order_id=entry_order_id,
                                #     sl_order_id=sl_order_id,
                                #     tp_order_id=tp_order_id,
                                # )
                                self.info_logger.info(f"fig_filename = self.__get_fig_filename")
                                # fig_filename = self.__get_fig_filename(
                                #     entry_price=self.ex_entry_price,
                                #     sl_price=self.ex_sl_price,
                                #     tp_price=self.ex_tp_price,
                                #     liq_price=self.ex_liq_price,
                                # )
                                self.info_logger.info(f"self.email_sender.email_new_order")
                                # self.email_sender.email_new_order(
                                #     message=message,
                                #     fig_filename=fig_filename,
                                # )
                                # self.info_logger.info(f"{message}")

                        except RejectedOrderError as e:
                            RejectedOrderError(f"RejectedOrderError for some reason ->{e.order_status}")
                        self.__set_ex_position_size_asset()
                        if self.ex_position_size_asset > 0:
                            self.info_logger.info(f"We are in a position ... checking to move stop loss")
                            try:
                                self.info_logger.info(f"self.order.check_move_stop_loss_to_be")
                                self.order.check_move_stop_loss_to_be(
                                    bar_index=bar_index,
                                    price_data=self.exchange.candles_np,
                                )
                                self.info_logger.info(f"no moving stop loss")
                                self.info_logger.info(f"self.order.check_move_trailing_stop_loss")
                                self.order.average_entry = self.__get_position_average_entry()
                                self.order.check_move_trailing_stop_loss(
                                    bar_index=bar_index,
                                    price_data=self.exchange.candles_np,
                                )
                                self.info_logger.info(f"no trail stop loss")
                            except RejectedOrderError as e:
                                pass
                            except MoveStopLoss as result:
                                try:
                                    self.info_logger.info(f"self.exchange.move_open_order")
                                    result_sl_price = self.order.round_size_by_tick_step(
                                        user_num=result.sl_price,
                                        exchange_num=self.exchange.exchange_settings.price_tick_step,
                                    )
                                    self.exchange.move_open_order(
                                        symbol=self.exchange.symbol,
                                        order_id=sl_order_id,
                                        new_price=result_sl_price,
                                    )
                                    self.exchange.get_open_order_by_order_id
                                    self.info_logger.info(
                                        f"trying to move the stop loss from {self.order.sl_price} to {result.sl_price}"
                                    )
                                    self.order.update_stop_loss_live_trading(sl_price=result.sl_price)
                                except KeyError as e:
                                    logging.error(f"Something wrong with move stop loss -> {e}")
                                    raise KeyError

                    except Exception as e:
                        logging.error(f"Something is wrong in the order creation part of live mode -> {e}")
                        raise Exception
                else:
                    self.info_logger.info("No entry ... waiting to get next bar")
            except Exception as e:
                logging.error(f"Something is wrong in the run part of live mode -> {e}")
                raise Exception(f"Something is wrong in the run part of live mode -> {e}")
            self.info_logger.info(f"Last Candle {self.exchange.last_fetched_time_to_pd_datetime()}")
            self.info_logger.info(
                f"Will sleep for {datetime.fromtimestamp(self.get_time_to_next_bar_seconds()).strftime('%M mins and %S seconds')} before getting next candles\n\n"
            )
            print(
                f"Will sleep for {datetime.fromtimestamp(self.get_time_to_next_bar_seconds()).strftime('%M mins and %S seconds')} before getting next candles"
            )
            sleep(self.get_time_to_next_bar_seconds())
        logging.error("Server stopped")

    def get_time_to_next_bar_seconds(self):
        ms_to_next_candle = max(
            0,
            (self.exchange.last_fetched_ms_time + self.exchange.timeframe_in_ms * 2)
            - self.exchange.get_current_time_ms(),
        )

        return int(ms_to_next_candle / 1000)

    def place_entry_order(self, asset_amount, entry_price):
        self.info_logger.info(f"Function: place_entry_order")
        return self.entry_order(
            asset_amount=asset_amount,
            price=entry_price,
        )

    def email_error_msg(self, msg):
        self.info_logger.info(f"Function: email_error_msg")
        self.email_sender.email_error_msg(msg=msg)

    def send_entry_email(self, entry_price, sl_price, tp_price, liq_price, body):
        self.info_logger.info(f"Function: send_entry_email")
        fig_filename = self.__get_plot_file(
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp_price,
            liq_price=liq_price,
        )
        self.info_logger.info(f"email_sender.email_new_order(body=body,")
        self.email_sender.email_new_order(body=body, fig_filename=fig_filename)

    def __get_fig_filename(self, entry_price, sl_price, tp_price, liq_price):
        self.info_logger.info(f"Function: __get_fig_filename")
        return self.strategy.return_plot_image(
            price_data=self.exchange.candles_df,
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp_price,
            liq_price=liq_price,
        )

    def __set_ex_position_size_asset(self):
        self.info_logger.info(f"Function: __set_ex_position_size_asset")
        self.ex_position_size_asset = float(self.get_position_info()["size"])

    def __set_ex_position_size_usd(self):
        self.info_logger.info(f"Function: __set_ex_position_size_asset")
        self.ex_position_size_usd = float(self.get_position_info()["positionValue"])

    def __get_position_average_entry(self):
        self.info_logger.info(f"Function: __set_ex_average_entry")
        return float(self.get_position_info()["entryPrice"])

    def __set_exchange_variables(self, entry_order_id, sl_order_id, tp_order_id):
        self.info_logger.info(f"Function: __set_exchange_variables")
        pos_info = self.get_position_info()
        entry_info = self.exchange.get_filled_orders_by_order_id(symbol=self.exchange.symbol, order_id=entry_order_id)
        tp_info = self.exchange.get_open_order_by_order_id(symbol=self.exchange.symbol, order_id=tp_order_id)
        sl_info = self.exchange.get_open_order_by_order_id(symbol=self.exchange.symbol, order_id=sl_order_id)

        self.ex_position_size_asset = float(pos_info.get("size"))
        self.ex_position_size_usd = float(pos_info.get("positionValue"))
        self.ex_average_entry = float(pos_info.get("entryPrice"))
        self.ex_entry_size_asset = float(entry_info.get("execQty"))
        self.ex_entry_size_usd = float(entry_info.get("execValue"))
        self.ex_entry_price = float(entry_info.get("execPrice"))
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
        self.info_logger.info(f"__get_pct_dif_above_average_entry(self, price, average_entry")
        return (price - average_entry) / average_entry

    def __get_pct_dif_below_average_entry(self, price, average_entry):
        self.info_logger.info(f"__get_pct_dif_below_average_entry(self, price, average_entry")
        return (average_entry - price) / average_entry

    def __create_entry_successful_message(self, entry_order_id, sl_order_id, tp_order_id):
        self.info_logger.info(f"__create_entry_successful_message(self, entry_order_id, sl_order_id, tp_order_id")
        self.__set_exchange_variables(
            entry_order_id=entry_order_id,
            sl_order_id=sl_order_id,
            tp_order_id=tp_order_id,
        )
        message = f"\
            An order was placed successfully\n\
            \
            User data ->        [average_entry={self.order.average_entry}]\n\
                                [position_size_usd={self.order.position_size_usd}]\n\
                                [entry_price={self.order.entry_price}]\n\
                                [entry_size_usd={self.order.entry_size_usd}]\n\
                                [leverage={self.order.leverage}]\n\
                                [liq price={self.order.liq_price}]\n\
                                [take_profit_price={self.order.tp_price}]\n\
                                [stop_loss_price={self.order.sl_price}]\n\
                                [possible loss={self.order.possible_loss}]\n\
                            \n\
            Exchange info ->    [candle_closing_price={self.exchange.candles_np[-1,3]}]\n\
                                [average_entry={self.order.average_entry}]\n\
                                [entry_price={self.order.entry_price}]\n\
                                [position_size_usd={self.order.position_size_usd}]\n\
                                [leverage={self.order.leverage}]\n\
                                [liq price={self.order.liq_price}]\n\
                                [entry_size_usd={self.order.entry_size_usd}]\n\
                                [take_profit_price={self.order.tp_price}]\n\
                                [stop_loss_price={self.order.sl_price}]\n\
                                [possible loss={self.ex_possible_loss}]\n"
        return message
