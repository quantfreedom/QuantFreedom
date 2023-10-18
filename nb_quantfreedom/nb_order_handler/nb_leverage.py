from numba.experimental import jitclass
import numpy as np

from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
from nb_quantfreedom.nb_order_handler.nb_price_getter import nb_GetMinPrice, nb_GetPrice
from nb_quantfreedom.np_enums import CandleBodyType, DecreasePosition, OrderStatus


class nb_Leverage:
    def __init__(self) -> None:
        pass

    def leverage_calculator(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        max_leverage: float,
        mmr_pct: float,
        sl_price: float,
        static_leverage: float,
    ):
        pass

    def check_liq_hit(
        self,
        bar_index: int,
        current_candle: np.array,
        exit_fee_pct: float,
        sl_price: float,
    ):
        pass

    def calc_long_liq_price(
        self,
        average_entry: float,
        entry_size_usd: float,
        leverage: float,
        mmr_pct: float,
        og_available_balance: float,
        og_cash_borrowed: float,
        og_cash_used: float,
        price_tick_step: float,
    ):
        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
        initial_margin = entry_size_usd / leverage
        fee_to_open = entry_size_usd * 0.0009  # math checked
        possible_bankruptcy_fee = entry_size_usd * (leverage - 1) / leverage * mmr_pct
        cash_used = initial_margin + fee_to_open + possible_bankruptcy_fee  # math checked

        if cash_used > og_available_balance:
            raise Exception(
                msg=f"Cash used={cash_used} > available_balance={og_available_balance}",
                order_status=1,
            )
        else:
            # liq formula
            # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
            available_balance = round(og_available_balance - cash_used, 4)
            cash_used = round(og_cash_used + cash_used, 4)
            cash_borrowed = round(og_cash_borrowed + entry_size_usd - cash_used, 4)

            liq_price = average_entry * (1 - (1 / leverage) + mmr_pct)  # math checked
            liq_price = nb_round_size_by_tick_step(
                user_num=liq_price,
                exchange_num=price_tick_step,
            )
            can_move_sl_to_be = True

        return (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            liq_price,
        )


@jitclass()
class nb_Long_SetStaticLeverage(nb_Leverage):
    def leverage_calculator(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        leverage_tick_step: float,
        max_leverage: float,
        mmr_pct: float,
        sl_price: float,
        static_leverage: float,
        price_tick_step: float,
    ):
        (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            liq_price,
        ) = self.calc_long_liq_price(
            leverage=static_leverage,
            entry_size_usd=entry_size_usd,
            average_entry=average_entry,
            og_cash_used=cash_used,
            og_available_balance=available_balance,
            og_cash_borrowed=cash_borrowed,
            mmr_pct=mmr_pct,
            price_tick_step=price_tick_step,
        )
        leverage = static_leverage
        return (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        )


@jitclass()
class nb_Long_CalcDynamicLeverage(nb_Leverage):
    def leverage_calculator(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        leverage_tick_step: float,
        max_leverage: float,
        mmr_pct: float,
        sl_price: float,
        static_leverage: float,
        price_tick_step: float,
    ):
        leverage = -average_entry / ((sl_price - sl_price * 0.001) - average_entry - mmr_pct * average_entry)
        leverage = nb_round_size_by_tick_step(
            user_num=leverage,
            exchange_num=leverage_tick_step,
        )
        if leverage > max_leverage:
            # print(f"Setting leverage from {leverage} to max leverage {max_leverage}")
            leverage = max_leverage
        elif leverage < 1:
            # print(f"Setting leverage from {leverage} to {1}")
            leverage = 1

        (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            liq_price,
        ) = self.calc_long_liq_price(
            leverage=leverage,
            entry_size_usd=entry_size_usd,
            average_entry=average_entry,
            mmr_pct=mmr_pct,
            og_cash_used=cash_used,
            og_available_balance=available_balance,
            og_cash_borrowed=cash_borrowed,
            price_tick_step=price_tick_step,
        )
        return (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        )


@jitclass
class nb_Long_Leverage(nb_Leverage):
    def check_liq_hit(
        self,
        current_candle: np.array,
        exit_fee_pct: float,
        liq_price: float,
    ):
        candle_low = nb_GetPrice().nb_price_getter(
            candle_body_type=CandleBodyType.Low,
            current_candle=current_candle,
        )
        if liq_price > candle_low:
            print(f"Stop loss hit")
            raise DecreasePosition(
                msg="Stop Loss hit",
                exit_price=liq_price,
                order_status=OrderStatus.StopLossFilled,
                exit_fee_pct=exit_fee_pct,
            )
        else:
            print(f"SL not hit")
