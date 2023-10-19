import numpy as np
from numba.experimental import jitclass

from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
from nb_quantfreedom.nb_order_handler.nb_price_getter import nb_GetMinPrice, nb_GetPrice, nb_PriceGetter
from nb_quantfreedom.nb_enums import CandleBodyType, DecreasePosition, MoveStopLoss, OrderStatus


class nb_StopLoss:
    def __init__(self):
        pass

    def nb_set_sl_to_z_or_e(
        self,
        average_entry,
        market_fee_pct,
        price_tick_step,
    ):
        pass

    def nb_sl_calculator(
        self,
        bar_index: int,
        based_on_lookback: int,
        candle_body: int,
        candles: np.array,
        price_getter: nb_PriceGetter,
        price_tick_step: float,
        sl_based_on_add_pct: float,
    ) -> float:
        pass

    def check_stop_loss_hit(
        self,
        bar_index: int,
        current_candle: np.array,
        exit_fee_pct: float,
        sl_price: float,
    ):
        pass

    def check_move_trailing_stop_loss(
        self,
        average_entry: float,
        bar_index: int,
        candles: np.array,
        trail_sl_when_pct_from_candle_body: float,
        trail_sl_by_pct: float,
        price_tick_step: float,
        candle_body: int,
        price_getter: nb_PriceGetter,
    ):
        pass

    def check_move_stop_loss_to_be(
        self,
        average_entry: float,
        bar_index: int,
        candles: np.array,
        can_move_sl_to_be: bool,
        sl_to_be_move_when_pct: float,
        candle_body: int,
        price_getter: nb_PriceGetter,
    ):
        pass


@jitclass()
class nb_Long_StopLoss(nb_StopLoss):
    def check_stop_loss_hit(
        self,
        current_candle: np.array,
        exit_fee_pct: float,
        sl_price: float,
    ):
        candle_low = nb_GetPrice().nb_price_getter(
            candle_body_type=CandleBodyType.Low,
            current_candle=current_candle,
        )
        if sl_price > candle_low:
            print(f"Stop loss hit")
            raise DecreasePosition(
                msg="Stop Loss hit",
                exit_price=sl_price,
                order_status=OrderStatus.StopLossFilled,
                exit_fee_pct=exit_fee_pct,
            )
        else:
            print(f"SL not hit")

    def check_move_stop_loss_to_be(
        self,
        average_entry: float,
        current_candle: np.array,
        can_move_sl_to_be: bool,
        sl_to_be_move_when_pct: float,
    ):
        if can_move_sl_to_be:
            print(f"Might move sotp to break even")
            # Stop Loss to break even
            candle_low = nb_GetPrice().nb_price_getter(
                candle_body_type=CandleBodyType.Low,
                current_candle=current_candle,
            )
            pct_from_ae = round((candle_low - average_entry) / average_entry, 2)
            move_sl = pct_from_ae > sl_to_be_move_when_pct
            if move_sl:
                old_sl = self.sl_price
                self.nb_set_sl_to_z_or_e(average_entry)
                print(
                    f"Moving sl pct_from_ae={pct_from_ae} > sl_to_be_move_when_pct={sl_to_be_move_when_pct} old sl={old_sl} new sl={self.sl_price}"
                )
                raise MoveStopLoss(
                    sl_price=self.sl_price,
                    order_status=OrderStatus.MovedStopLossToBE,
                )
            else:
                print(f"not moving sl to be")
        else:
            print(f"not moving sl to be")

    def check_move_trailing_stop_loss(
        self,
        average_entry: float,
        bar_index: int,
        current_candle: np.array,
        trail_sl_when_pct_from_candle_body: float,
        trail_sl_by_pct: float,
        price_tick_step: float,
        candle_body_type: CandleBodyType,
        price_getter: nb_PriceGetter,
    ):
        candle_body_ohlc = price_getter.nb_price_getter(
            candle_body_type=candle_body_type,
            lookback=bar_index,
            bar_index=bar_index + 1,
            current_candle=current_candle,
        )
        pct_from_ae = round((candle_body_ohlc - average_entry) / average_entry, 2)
        possible_move_tsl = pct_from_ae > trail_sl_when_pct_from_candle_body
        if possible_move_tsl:
            print(
                f"Maybe moving tsl pct_from_ae={pct_from_ae} > trail_sl_when_pct_from_candle_body={trail_sl_when_pct_from_candle_body}"
            )
            temp_sl_price = candle_body_ohlc - candle_body_ohlc * trail_sl_by_pct
            temp_sl_price = nb_round_size_by_tick_step(
                user_num=temp_sl_price,
                exchange_num=price_tick_step,
            )
            if temp_sl_price > self.sl_price:
                print(f"temp sl {temp_sl_price} > sl price {self.sl_price} - Will move trailing stop")
                self.sl_price = temp_sl_price
                raise MoveStopLoss(
                    sl_price=self.sl_price,
                    order_status=OrderStatus.MovedTrailingStopLoss,
                )
            else:
                print(f"Wont move tsl temp sl {temp_sl_price} < sl price {self.sl_price}")
        else:
            print(f"Not moving tsl")


@jitclass()
class nb_Long_SLToZero(nb_StopLoss):
    def nb_set_sl_to_z_or_e(self, average_entry, market_fee_pct, price_tick_step):
        sl_price = (market_fee_pct * average_entry + average_entry) / (1 - market_fee_pct)
        sl_price = nb_round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=price_tick_step,
        )
        print(f"New sl_price={self.sl_price}")
        return sl_price


@jitclass()
class nb_Long_SLToEntry(nb_StopLoss):
    def nb_set_sl_to_z_or_e(self, average_entry, market_fee_pct, price_tick_step):
        sl_price = average_entry
        print(f"New sl_price={sl_price}")
        return sl_price


@jitclass()
class nb_Long_SLCandleBody(nb_StopLoss):
    def nb_sl_calculator(
        self,
        bar_index: int,
        based_on_lookback: int,
        candle_body: int,
        candles: np.array,
        price_getter: nb_PriceGetter,
        price_tick_step: float,
        sl_based_on_add_pct: float,
    ) -> float:
        # lb will be bar index if sl isn't based on lookback because look back will be 0
        lookback = max(bar_index - based_on_lookback, 0)
        candle_body = price_getter.nb_price_getter(
            candle_body=candle_body,
            lookback=lookback,
            bar_index=bar_index,
            candles=candles,
        )
        sl_price = candle_body - (candle_body * sl_based_on_add_pct)
        sl_price = nb_round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=price_tick_step,
        )
        print(f"sl_price = {sl_price}")
        return sl_price
