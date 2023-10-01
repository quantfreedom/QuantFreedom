import logging
from time import sleep
from uuid import uuid4
from quantfreedom.enums import LongOrShortType, MoveStopLoss, OrderPlacementType, RejectedOrderError

from quantfreedom.exchanges.exchange import Exchange
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
    ):
        self.exchange = exchange
        self.candles_to_dl = candles_to_dl
        self.strategy = strategy
        self.order = order

        if self.exchange.long_or_short == LongOrShortType.Long:
            self.sl_order = self.exchange.create_long_sl_order
            if entry_order_type == OrderPlacementType.Market:
                self.check_entry_order = self.exchange.check_if_order_filled
                self.entry_order = self.exchange.create_long_entry_market_order
            else:
                self.check_entry_order = self.exchange.check_if_order_active
                self.entry_order = self.exchange.create_long_entry_limit_order

            if tp_order_type == OrderPlacementType.Market:
                self.tp_order = self.exchange.create_long_tp_market_order
            else:
                self.tp_order = self.exchange.create_long_tp_limit_order

    def run(self):
        entry_order_id = 0
        tp_order_id = 0
        sl_order_id = 0

        self.exchange.set_init_last_fetched_time()
        logging.info(f"Last Candle {self.exchange.__last_fetched_time_to_pd_datetime()}")
        logging.info(
            f"Will sleep for {round(self.time_to_sleep_seconds/60,2)} minutes before getting first batch of candles"
        )

        sleep(self.__get_time_to_next_bar_seconds())
        while True:
            try:
                price_data = self.exchange.get_and_set_candles_df()[["open", "high", "low", "close"]].values

                # bar_index bar index is always the last bar ... so if we have 200 candles we are at index 200
                bar_index = price_data.shape()[0]

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
                            if not self.cancel_tp_and_sl(tp_order_id=tp_order_id, sl_order_id=sl_order_id):
                                if self.exchange.in_position:
                                    logging.error("Wasn't able to verify that the tp and sl were canceled")
                            entry_order_id, _ = self.place_entry_order(
                                asset_amount=self.order.entry_size / self.order.entry_price,
                                entry_price=self.order.entry_price,
                            )
                            sleep(0.2)
                            if not self.check_entry_order(order_id=entry_order_id):
                                raise LookupError(f"Couldn't verify entry order was filled")
                            
                            
                            #### place stop loss and tp and also check if they were placed
                            
                            
                            
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
                                #####
                                # here we adjust the stop
                                #####
                    except Exception as e:
                        logging.error(f"Something is wrong in the order creation part of live mode -> {e}")
                        raise Exception
                else:
                    logging.info("No entry ... waiting to get next bar")
            except Exception as e:
                logging.error(f"Something is wrong in the run part of live mode -> {e}")
                raise Exception
            sleep(self.__get_time_to_next_bar_seconds())

    def __get_time_to_next_bar_seconds(self):
        ms_to_next_candle = max(
            0,
            (self.exchange.last_fetched_ms_time + self.exchange.timeframe_in_ms * 2)
            - self.exchange.__get_ms_current_time(),
        )
        time_to_sleep_seconds = ms_to_next_candle / 1000.0

        logging.debug(
            f"[last_fetched_time={self.exchange.__last_fetched_time_to_pd_datetime()}]\n\
                        [bar_duration={self.exchange.timeframe_in_ms/1000}]\n\
                        [now={self.exchange.__get_current_pd_datetime()}]\n\
                        [secs_to_next_candle={time_to_sleep_seconds}]\n\
                        [mins_to_next_candle={round(time_to_sleep_seconds/60,2)}]\n"
        )
        return time_to_sleep_seconds

    def place_entry_order(self, qty, orderLinkId, entry_price):
        self.entry_order(
            qty=qty,
            orderLinkId=orderLinkId,
            price=entry_price,
        )
        pass

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
