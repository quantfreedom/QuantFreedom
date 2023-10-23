from numba.experimental import jitclass
import numpy as np
from nb_quantfreedom.nb_custom_logger import CustomLoggerClass
from nb_quantfreedom.nb_enums import CandleBodyType, DecreasePosition, OrderStatus

from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
from nb_quantfreedom.nb_order_handler.nb_class_helpers import nb_GetPrice


class LeverageClass:
    def __init__(self) -> None:
        pass

    def calculate_leverage(
        self,
        logger: CustomLoggerClass,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        max_leverage: float,
        min_leverage: float,
        mmr_pct: float,
        sl_price: float,
        static_leverage: float,
    ):
        pass

    def check_liq_hit(
        self,
        logger: CustomLoggerClass,
        bar_index: int,
        current_candle: np.array,
        sl_price: float,
    ):
        pass

    def calc_liq_price(
        self,
        logger: CustomLoggerClass,
        average_entry: float,
        entry_size_usd: float,
        leverage: float,
        mmr_pct: float,
        og_available_balance: float,
        og_cash_borrowed: float,
        og_cash_used: float,
        price_tick_step: float,
    ):
        pass


@jitclass()
class LeverageNB(LeverageClass):
    def __init__(self) -> None:
        pass

    def calculate_leverage(
        self,
        logger: CustomLoggerClass,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        max_leverage: float,
        min_leverage: float,
        mmr_pct: float,
        sl_price: float,
        static_leverage: float,
    ):
        pass

    def check_liq_hit(
        self,
        logger: CustomLoggerClass,
        bar_index: int,
        current_candle: np.array,
        sl_price: float,
    ):
        pass

    def calc_liq_price(
        self,
        logger: CustomLoggerClass,
        average_entry: float,
        entry_size_usd: float,
        leverage: float,
        mmr_pct: float,
        og_available_balance: float,
        og_cash_borrowed: float,
        og_cash_used: float,
        price_tick_step: float,
    ):
        pass


@jitclass()
class nb_Long_SLev(LeverageClass):
    def calculate_leverage(
        self,
        logger: CustomLoggerClass,
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
        ) = nb_Long_Leverage().calc_liq_price(
            logger=logger,
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
        logger.log_debug(
            "nb_leverage.py - nb_Long_SLev - calculate_leverage() - Lev set to static lev= "
            + logger.float_to_str(leverage)
        )
        return (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        )


@jitclass()
class nb_Long_DLev(LeverageClass):
    """
    Calculate dynamic leverage
    """

    def calculate_leverage(
        self,
        logger: CustomLoggerClass,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        leverage_tick_step: float,
        max_leverage: float,
        min_leverage: float,
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
            logger.log_debug(
                "nb_leverage.py - nb_Long_DLev - calculate_leverage() - Lev too high"
                + " Old Lev= "
                + logger.float_to_str(leverage)
                + " Max Lev= "
                + logger.float_to_str(max_leverage)
            )
            leverage = max_leverage
        elif leverage < min_leverage:
            logger.log_debug(
                "nb_leverage.py - nb_Long_DLev - calculate_leverage() - Lev too low"
                + " Old Lev= "
                + logger.float_to_str(leverage)
                + " Min Lev= "
                + logger.float_to_str(min_leverage)
            )
            leverage = 1
        else:
            logger.log_debug(
                "nb_leverage.py - nb_Long_DLev - calculate_leverage() -" + " Leverage= " + logger.float_to_str(leverage)
            )

        (
            available_balance,
            cash_borrowed,
            cash_used,
            liq_price,
        ) = nb_Long_Leverage().calc_liq_price(
            logger=logger,
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
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        )


@jitclass
class nb_Long_Leverage(LeverageClass):
    def check_liq_hit(
        self,
        logger: CustomLoggerClass,
        current_candle: np.array,
        liq_price: float,
    ):
        candle_low = nb_GetPrice().nb_price_getter(
            logger=logger,
            candle_body_type=CandleBodyType.Low,
            current_candle=current_candle,
        )
        if liq_price > candle_low:
            logger.log_debug("nb_leverage.py - nb_Long_Leverage - check_liq_hit() - Liq Hit")
            return True
        else:
            logger.log_debug("nb_leverage.py - nb_Long_Leverage - check_liq_hit() - No hit on liq price")
            return False

    def calc_liq_price(
        self,
        logger: CustomLoggerClass,
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
        logger.log_debug(
            "nb_leverage.py - nb_Long_Leverage - calc_liq_price() -"
            + "\ninitial_margin= "
            + logger.float_to_str(round(initial_margin, 3))
            + "\nfee_to_open= "
            + logger.float_to_str(round(fee_to_open, 3))
            + "\npossible_bankruptcy_fee= "
            + logger.float_to_str(round(possible_bankruptcy_fee, 3))
            + "\ncash_used= "
            + logger.float_to_str(round(cash_used, 3))
        )

        if cash_used > og_available_balance:
            logger.log_warning(
                "nb_leverage.py - nb_Long_Leverage - calc_liq_price() - Cash used bigger than available balance"
            )
            raise Exception
        else:
            # liq formula
            # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
            available_balance = round(og_available_balance - cash_used, 3)
            cash_used = round(og_cash_used + cash_used, 3)
            cash_borrowed = round(og_cash_borrowed + entry_size_usd - cash_used, 3)

            liq_price = average_entry * (1 - (1 / leverage) + mmr_pct)  # math checked
            liq_price = nb_round_size_by_tick_step(
                user_num=liq_price,
                exchange_num=price_tick_step,
            )
            logger.log_debug(
                "nb_leverage.py - nb_Long_Leverage - calc_liq_price() -"
                + "\navailable_balance= "
                + logger.float_to_str(available_balance)
                + "\nnew cash_used= "
                + logger.float_to_str(cash_used)
                + "\ncash_borrowed= "
                + logger.float_to_str(cash_borrowed)
                + "\nliq_price= "
                + logger.float_to_str(liq_price)
            )

        return (
            available_balance,
            cash_borrowed,
            cash_used,
            liq_price,
        )
