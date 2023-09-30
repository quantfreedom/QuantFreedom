import logging
from time import sleep
from quantfreedom.enums import MoveStopLoss, RejectedOrderError

from quantfreedom.exchanges.exchange import Exchange
from quantfreedom.gather_order_ex_info.long_short_orders import Order
from quantfreedom.strategies.strategy import Strategy


class LiveTrading:
    def __init__(
        self,
        exchange: Exchange,
        candles_to_dl: int,
        strategy: Strategy,
        order: Order,
    ) -> None:
        self.exchange = exchange
        self.candles_to_dl = candles_to_dl
        self.strategy = strategy
        self.order = order
        pass

    def run(self):
        self.exchange.__set_init_last_fetched_time()
        logging.info(f"Last Candle {self.exchange.__last_fetched_time_to_pd_datetime()}")
        logging.info(
            f"Will sleep for {round(self.time_to_sleep_seconds/60,2)} minutes before getting first batch of candles"
        )

        sleep(self.__get_time_to_next_bar_seconds())
        while True:
            try:
                self.exchange.set_candles_df()
                self.strategy.set_indicator_live_trading(self.exchange.candles_df)
                if self.strategy.evaluate():
                    try:
                        if self.exchange.get_position_info()["position_size"] < 1000:
                            try:
                                self.order.calculate_stop_loss(
                                    bar_index=bar_index,
                                    price_data=price_data,
                                )
                                self.order.calculate_increase_posotion(
                                    entry_price=price_data[
                                        bar_index, 0
                                    ]  # entry price is open because we are getting the signal from the close of the previous candle
                                )
                                self.order.calculate_leverage()
                                self.order.calculate_take_profit()
                                #####
                                # here we need to actually excute the order
                                #####
                            except RejectedOrderError as e:
                                pass
                        if self.exchange.get_position_info()["position_size"] > 0:
                            try:
                                self.order.check_move_stop_loss_to_be(bar_index=bar_index, price_data=price_data)
                                self.order.check_move_trailing_stop_loss(bar_index=bar_index, price_data=price_data)
                            except RejectedOrderError as e:
                                pass
                            except MoveStopLoss as e:
                                self.order.move_stop_loss(
                                    sl_price=e.sl_price,
                                    order_status=e.order_status,
                                    bar_index=bar_index,
                                    order_settings_index=order_settings_index,
                                    indicator_settings_index=indicator_settings_index,
                                )
                                #####
                                # here we adjust the stop
                                #####
                    except Exception as e:
                        logging.error(f"Something is wrong in the order creation part of live mode -> {repr(e)}")
                        raise Exception
                else:
                    logging.info("No entry ... waiting to get next bar")
            except Exception as e:
                logging.error(f"Something is wrong in the run part of live mode -> {repr(e)}")
                raise Exception
            sleep(self.__get_time_to_next_bar_seconds())

    def __get_time_to_next_bar_seconds(self):
        ms_to_next_candle = max(
            0,
            (self.last_fetched_time + self.exchange.timeframe_in_ms * 2) - self.__get_ms_current_time(),
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
