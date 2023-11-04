import numpy as np
import logging

from quantfreedom.helper_funcs import round_size_by_tick_step
from quantfreedom.enums import (
    AccountState,
    CandleBodyType,
    MoveStopLoss,
    OrderResult,
    OrderStatus,
    PriceGetterType,
    StopLossStrategyType,
    ZeroOrEntryType,
)

logger = logging.getLogger("info")


class LongStopLoss:
    candle_body_type: CandleBodyType
    sl_to_be_cb_type: int
    sl_to_be_move_when_pct: float

    def __init__(
        self,
        sl_strategy_type: StopLossStrategyType,
        pg_min_max_sl_bcb: PriceGetterType,
        sl_to_be_bool: bool,
        z_or_e_type: ZeroOrEntryType,
        trail_sl_bool: bool,
        market_fee_pct: float,
        price_tick_step: float,
    ) -> None:
        self.market_fee_pct = market_fee_pct
        self.price_tick_step = price_tick_step

        # stop loss calulator
        if sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
            self.sl_calculator = self.long_sl_bcb
            self.checker_sl_hit = self.long_c_sl_hit
            if pg_min_max_sl_bcb == PriceGetterType.Min:
                self.sl_bcb_price_getter = self.min_price_getter
            elif pg_min_max_sl_bcb == PriceGetterType.Max:
                self.sl_bcb_price_getter = self.max_price_getter

        # SL break even
        if sl_to_be_bool:
            self.checker_sl_to_be = self.long_cm_sl_to_be
            # setting up stop loss be zero or entry
            if z_or_e_type == ZeroOrEntryType.ZeroLoss:
                self.zero_or_entry_calc = self.long_sl_to_zero
            elif z_or_e_type == ZeroOrEntryType.AverageEntry:
                self.zero_or_entry_calc = self.sl_to_entry
        else:
            # self.checker_sl_to_be = long_cm_sl_to_be_pass
            # self.zero_or_entry_calc = sl_to_z_e_pass
            self.checker_sl_to_be = self.pass_func
            self.zero_or_entry_calc = self.pass_func

        # Trailing stop loss
        if trail_sl_bool:
            self.checker_tsl = self.long_cm_tsl
        else:
            # self.checker_tsl = long_cm_tsl_pass
            self.checker_tsl = self.pass_func

        if trail_sl_bool or sl_to_be_bool:
            self.sl_mover = self.move_stop_loss
        else:
            # self.sl_mover = move_stop_loss_pass
            self.sl_mover = self.pass_func

    def sl_to_entry(
        self,
        average_entry,
    ):
        sl_price = average_entry
        return sl_price

    def long_sl_to_zero(
        self,
        average_entry,
    ):
        sl_price = (self.market_fee_pct * average_entry + average_entry) / (1 - self.market_fee_pct)
        sl_price = round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=self.price_tick_step,
        )

        return sl_price

    def min_price_getter(
        self,
        bar_index: int,
        candles: np.array,
        lookback: int,
    ) -> float:
        price = candles[lookback : bar_index + 1, self.candle_body_type].min()
        return price

    def max_price_getter(
        self,
        bar_index: int,
        candles: np.array,
        lookback: int,
    ) -> float:
        price = candles[lookback : bar_index + 1, self.candle_body_type].max()
        return price

    def long_c_sl_hit(
        self,
        current_candle: np.array,
        sl_price: float,
    ):
        logger.debug("Starting")
        candle_low = current_candle[CandleBodyType.Low]
        logger.debug(f"candle_low= {candle_low}")
        if sl_price > candle_low:
            logger.debug("Stop loss hit")
            return True
        else:
            logger.debug("No hit on stop loss")
            return False

    def long_cm_sl_to_be_pass(self, **vargs):
        """
        Long stop loss to break even pass
        """
        pass

    def long_cm_sl_to_be(
        self,
        average_entry: float,
        can_move_sl_to_be: bool,
        current_candle: np.array,
        sl_price: float,
    ):
        """
        Checking to see if we move the stop loss to break even
        """
        if can_move_sl_to_be:
            logger.debug("Might move sl to break even")
            # Stop Loss to break even
            candle_body = current_candle[self.sl_to_be_cb_type]
            pct_from_ae = (candle_body - average_entry) / average_entry
            logger.debug("pct_from_ae= {round(pct_from_ae * 100, 4)}")
            move_sl = pct_from_ae > self.sl_to_be_move_when_pct
            if move_sl:
                old_sl = sl_price
                sl_price = self.zero_or_entry_calc(average_entry=average_entry)
                logger.debug(f"moving old_sl= {old_sl} to new sl= {sl_price}")
                raise MoveStopLoss(
                    sl_price=sl_price,
                    order_status=OrderStatus.MovedSLToBE,
                )
            else:
                logger.debug("not moving sl to be")
        else:
            logger.debug("can't move sl to be")

    def long_cm_tsl_pass(self, **vargs):
        return 0.0

    def long_cm_tsl(
        self,
        average_entry: float,
        candle_body_type: CandleBodyType,
        current_candle: np.array,
        price_tick_step: float,
        sl_price: float,
        trail_sl_by_pct: float,
        trail_sl_when_pct: float,
    ):
        """
        Checking to see if we move the trailing stop loss
        """
        candle_body = current_candle[candle_body_type]
        pct_from_ae = (candle_body - average_entry) / average_entry
        logger.debug(f"pct_from_ae= {round(pct_from_ae * 100, 4)}")
        possible_move_tsl = pct_from_ae > trail_sl_when_pct
        if possible_move_tsl:
            logger.debug("Maybe move tsl")
            temp_sl_price = candle_body - candle_body * trail_sl_by_pct
            temp_sl_price = round_size_by_tick_step(
                user_num=temp_sl_price,
                exchange_num=price_tick_step,
            )
            logger.debug(f"temp sl= {temp_sl_price}")
            if temp_sl_price > sl_price:
                logger.debug(f"Moving tsl new sl= {temp_sl_price} > old sl= {sl_price}")
                return temp_sl_price
            else:
                logger.debug("Wont move tsl")
                return 0.0
        else:
            logger.debug("Not moving tsl")
            return 0.0

    def long_sl_bcb(
        self,
        bar_index: int,
        candles: np.array,
        price_tick_step: float,
        sl_based_on_add_pct: float,
        sl_based_on_lookback: int,
        sl_bcb_price_getter,
        sl_bcb_type: int,
    ) -> float:
        """
        Long Stop Loss Based on Candle Body Calculator
        """
        # lb will be bar index if sl isn't based on lookback because look back will be 0
        lookback = max(bar_index - sl_based_on_lookback, 0)
        logger.debug(f"lookback= {lookback}")
        candle_body = sl_bcb_price_getter(
            bar_index=bar_index,
            candles=candles,
            candle_body_type=sl_bcb_type,
            lookback=lookback,
        )
        logger.debug(f"candle_body= {candle_body}")
        sl_price = candle_body - (candle_body * sl_based_on_add_pct)
        sl_price = round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=price_tick_step,
        )
        logger.debug(f"sl_price= {sl_price}")
        return sl_price

    def move_stop_loss(
        self,
        account_state: AccountState,
        bar_index: int,
        can_move_sl_to_be: bool,
        dos_index: int,
        ind_set_index: int,
        order_result: OrderResult,
        order_status: int,
        sl_price: float,
        timestamp: int,
    ) -> OrderResult:
        account_state = AccountState(
            # where we are at
            ind_set_index=ind_set_index,
            dos_index=dos_index,
            bar_index=bar_index,
            timestamp=timestamp,
            # account info
            available_balance=account_state.available_balance,
            cash_borrowed=account_state.cash_borrowed,
            cash_used=account_state.cash_used,
            equity=account_state.equity,
            fees_paid=account_state.fees_paid,
            possible_loss=account_state.possible_loss,
            realized_pnl=account_state.realized_pnl,
            total_trades=account_state.total_trades,
        )
        logger.debug("created account state")
        sl_pct = abs(round((order_result.average_entry - sl_price) / order_result.average_entry, 4))
        logger.debug(f"sl percent= {sl_pct}")
        order_result = OrderResult(
            average_entry=order_result.average_entry,
            can_move_sl_to_be=can_move_sl_to_be,
            entry_price=order_result.entry_price,
            entry_size_asset=order_result.entry_size_asset,
            entry_size_usd=order_result.entry_size_usd,
            exit_price=order_result.exit_price,
            leverage=order_result.leverage,
            liq_price=order_result.liq_price,
            order_status=order_status,
            position_size_asset=order_result.position_size_asset,
            position_size_usd=order_result.position_size_usd,
            sl_pct=sl_pct,
            sl_price=sl_price,
            tp_pct=order_result.tp_pct,
            tp_price=order_result.tp_price,
        )
        logger.debug("created order result")

        return account_state, order_result

    def move_stop_loss_pass(
        account_state: AccountState,
        bar_index: int,
        can_move_sl_to_be: bool,
        dos_index: int,
        ind_set_index: int,
        order_result: OrderResult,
        order_status: int,
        sl_price: float,
        timestamp: int,
    ) -> OrderResult:
        return account_state, order_result

    def pass_func(self, **vargs):
        pass
