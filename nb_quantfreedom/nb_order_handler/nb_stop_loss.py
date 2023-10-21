import numpy as np
from numba.experimental import jitclass
from nb_quantfreedom.nb_custom_logger import CustomLoggerNB

from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
from nb_quantfreedom.nb_enums import CandleBodyType, DecreasePosition, MoveStopLoss, OrderResults, OrderStatus
from nb_quantfreedom.nb_order_handler.nb_class_helpers import PriceGetterNB, ZeroOrEntryNB, nb_GetPrice


class StopLossClass:
    def __init__(self):
        pass

    def move_stop_loss(
        self,
        logger: CustomLoggerNB,
        bar_index: int,
        can_move_sl_to_be: bool,
        dos_index: int,
        ind_set_index: int,
        order_results: OrderResults,
        order_status: int,
        sl_price: float,
        timestamp: int,
    ):
        pass

    def calculate_stop_loss(
        self,
        logger: CustomLoggerNB,
        bar_index: int,
        candles: np.array,
        price_tick_step: float,
        sl_based_on_add_pct: float,
        sl_based_on_lookback: int,
        sl_bcb_price_getter: PriceGetterNB,
        sl_bcb_type: int,
    ):
        pass

    def check_stop_loss_hit(
        self,
        logger: CustomLoggerNB,
        bar_index: int,
        current_candle: np.array,
        exit_fee_pct: float,
        sl_price: float,
    ):
        pass

    def check_move_stop_loss_to_be(
        self,
        logger: CustomLoggerNB,
        average_entry: float,
        can_move_sl_to_be: bool,
        candle_body_type: int,
        current_candle: np.array,
        set_z_e: ZeroOrEntryNB,
        sl_price: float,
        sl_to_be_move_when_pct: float,
        market_fee_pct: float,
        price_tick_step: float,
    ):
        pass

    def check_move_trailing_stop_loss(
        self,
        logger: CustomLoggerNB,
        average_entry: float,
        candle_body_type: int,
        can_move_sl_to_be: bool,
        current_candle: np.array,
        price_tick_step: float,
        sl_price: float,
        trail_sl_by_pct: float,
        trail_sl_when_pct: float,
    ):
        pass


@jitclass()
class StopLossNB(StopLossClass):
    def move_stop_loss(
        self,
        logger: CustomLoggerNB,
        bar_index: int,
        can_move_sl_to_be: bool,
        dos_index: int,
        ind_set_index: int,
        order_results: OrderResults,
        order_status: int,
        sl_price: float,
        timestamp: int,
    ):
        pass

    def calculate_stop_loss(
        self,
        logger: CustomLoggerNB,
        bar_index: int,
        candles: np.array,
        price_tick_step: float,
        sl_based_on_add_pct: float,
        sl_based_on_lookback: int,
        sl_bcb_price_getter: PriceGetterNB,
        sl_bcb_type: int,
    ):
        pass

    def check_stop_loss_hit(
        self,
        logger: CustomLoggerNB,
        bar_index: int,
        current_candle: np.array,
        exit_fee_pct: float,
        sl_price: float,
    ):
        pass

    def check_move_stop_loss_to_be(
        self,
        logger: CustomLoggerNB,
        average_entry: float,
        can_move_sl_to_be: bool,
        candle_body_type: int,
        current_candle: np.array,
        set_z_e: ZeroOrEntryNB,
        sl_price: float,
        sl_to_be_move_when_pct: float,
        market_fee_pct: float,
        price_tick_step: float,
    ):
        pass

    def check_move_trailing_stop_loss(
        self,
        logger: CustomLoggerNB,
        average_entry: float,
        candle_body_type: int,
        can_move_sl_to_be: bool,
        current_candle: np.array,
        price_tick_step: float,
        sl_price: float,
        trail_sl_by_pct: float,
        trail_sl_when_pct: float,
    ):
        pass


@jitclass()
class nb_Long_StopLoss(StopLossClass):
    def check_stop_loss_hit(
        self,
        logger: CustomLoggerNB,
        current_candle: np.array,
        exit_fee_pct: float,
        sl_price: float,
    ):
        logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - Starting")
        candle_low = nb_GetPrice().nb_price_getter(
            logger=logger,
            candle_body_type=CandleBodyType.Low,
            current_candle=current_candle,
        )
        if sl_price > candle_low:
            logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - Stop loss hit")
            raise DecreasePosition(
                msg="Stop Loss hit",
                exit_price=sl_price,
                order_status=OrderStatus.StopLossFilled,
                exit_fee_pct=exit_fee_pct,
            )
        else:
            logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - SL not hit")

    def check_move_stop_loss_to_be(
        self,
        logger: CustomLoggerNB,
        average_entry: float,
        can_move_sl_to_be: bool,
        candle_body_type: int,
        current_candle: np.array,
        set_z_e: ZeroOrEntryNB,
        sl_price: float,
        sl_to_be_move_when_pct: float,
        market_fee_pct: float,
        price_tick_step: float,
    ):
        if can_move_sl_to_be:
            logger.log_debug(
                "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - Might move sotp to break even"
            )
            # Stop Loss to break even
            candle_low = nb_GetPrice().nb_price_getter(
                logger=logger,
                candle_body_type=candle_body_type,
                current_candle=current_candle,
            )
            pct_from_ae = (candle_low - average_entry) / average_entry
            move_sl = pct_from_ae > sl_to_be_move_when_pct
            if move_sl:
                old_sl = sl_price
                set_z_e.nb_set_sl_to_z_or_e(
                    average_entry=average_entry,
                    market_fee_pct=market_fee_pct,
                    price_tick_step=price_tick_step,
                )
                logger.log_debug(
                    "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - pct_from_ae={round(pct_from_ae*100,4)} > sl_to_be_move_when_pct={round(sl_to_be_move_when_pct*100,4)} old sl={old_sl} new sl={sl_price}"
                )
                raise MoveStopLoss(
                    sl_price=sl_price,
                    order_status=OrderStatus.MovedSLToBE,
                    can_move_sl_to_be=can_move_sl_to_be,
                )
            else:
                logger.log_debug(
                    "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - not moving sl to be"
                )
        else:
            logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - not moving sl to be")

    def check_move_trailing_stop_loss(
        self,
        logger: CustomLoggerNB,
        average_entry: float,
        can_move_sl_to_be: bool,
        candle_body_type: CandleBodyType,
        current_candle: np.array,
        price_tick_step: float,
        sl_price: float,
        trail_sl_by_pct: float,
        trail_sl_when_pct: float,
    ):
        candle_low = nb_GetPrice().nb_price_getter(
            logger=logger,
            candle_body_type=candle_body_type,
            current_candle=current_candle,
        )
        pct_from_ae = (candle_low - average_entry) / average_entry
        possible_move_tsl = pct_from_ae > trail_sl_when_pct
        if possible_move_tsl:
            logger.log_debug(
                "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Maybe Move pct_from_ae={round(pct_from_ae*100,4)} > trail_sl_when_pct={round(trail_sl_when_pct * 100,4)}"
            )
            temp_sl_price = candle_low - candle_low * trail_sl_by_pct
            temp_sl_price = nb_round_size_by_tick_step(
                user_num=temp_sl_price,
                exchange_num=price_tick_step,
            )
            if temp_sl_price > sl_price:
                logger.log_debug(
                    "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Will move trailing stop temp sl=temp_sl_price} > sl price=sl_price}"
                )
                sl_price = temp_sl_price
                raise MoveStopLoss(
                    sl_price=sl_price,
                    order_status=OrderStatus.MovedTSL,
                    can_move_sl_to_be=can_move_sl_to_be,
                )
            else:
                logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Wont move tsl")
        else:
            logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Not moving tsl")


@jitclass()
class nb_Long_SLBCB(StopLossClass):
    """
    Stop loss based on candle body
    """

    def calculate_stop_loss(
        self,
        logger: CustomLoggerNB,
        bar_index: int,
        candles: np.array,
        price_tick_step: float,
        sl_based_on_add_pct: float,
        sl_based_on_lookback: int,
        sl_bcb_price_getter: PriceGetterNB,
        sl_bcb_type: int,
    ) -> float:
        # lb will be bar index if sl isn't based on lookback because look back will be 0
        lookback = max(bar_index - sl_based_on_lookback, 0)
        candle_body = sl_bcb_price_getter.nb_min_max_price_getter(
            logger=logger,
            candle_body_type=sl_bcb_type,
            lookback=lookback,
            bar_index=bar_index,
            candles=candles,
        )
        sl_price = candle_body - (candle_body * sl_based_on_add_pct)
        sl_price = nb_round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=price_tick_step,
        )
        logger.log_debug("nb_stop_loss.py - nb_Long_SLBCB - calculate_stop_loss() - sl_price=sl_price}")
        return sl_price


@jitclass()
class nb_MoveSL(StopLossClass):
    def move_stop_loss(
        self,
        logger: CustomLoggerNB,
        bar_index: int,
        can_move_sl_to_be: bool,
        dos_index: int,
        ind_set_index: int,
        order_results: OrderResults,
        order_status: int,
        sl_price: float,
        timestamp: int,
    ) -> OrderResults:
        return OrderResults(
            # where we are at
            ind_set_index=ind_set_index,
            dos_index=dos_index,
            bar_index=bar_index,
            timestamp=timestamp,
            # account info
            equity=order_results.equity,
            available_balance=order_results.available_balance,
            cash_borrowed=order_results.cash_borrowed,
            cash_used=order_results.cash_used,
            # order info
            average_entry=order_results.average_entry,
            can_move_sl_to_be=can_move_sl_to_be,
            fees_paid=order_results.fees_paid,
            leverage=order_results.leverage,
            liq_price=order_results.liq_price,
            order_status=order_status,
            possible_loss=order_results.possible_loss,
            entry_size_asset=order_results.entry_size_asset,
            entry_size_usd=order_results.entry_size_usd,
            entry_price=order_results.entry_price,
            exit_price=order_results.exit_price,
            position_size_asset=order_results.position_size_asset,
            position_size_usd=order_results.position_size_usd,
            realized_pnl=order_results.realized_pnl,
            sl_pct=abs(round((order_results.average_entry - sl_price) / order_results.average_entry, 4)),
            sl_price=sl_price,
            total_trades=order_results.total_trades,
            tp_pct=order_results.tp_pct,
            tp_price=order_results.tp_price,
        )
