import numpy as np
from logging import getLogger
from quantfreedom.enums import CandleBodyType, DecreasePosition, LeverageStrategyType, OrderStatus
from quantfreedom.helper_funcs import round_size_by_tick_step

logger = getLogger("info")


class LongLeverage:
    static_leverage: float

    def __init__(
        self,
        leverage_strategy_type: LeverageStrategyType,
        leverage_tick_step: float,
        market_fee_pct: float,
        max_leverage: float,
        min_leverage: float,
        mmr_pct: float,
        price_tick_step: float,
    ):
        self.min_leverage = min_leverage
        self.price_tick_step = price_tick_step
        self.leverage_tick_step = leverage_tick_step
        self.max_leverage = max_leverage
        self.mmr_pct = mmr_pct
        self.market_fee_pct = market_fee_pct

        if leverage_strategy_type == LeverageStrategyType.Dynamic:
            self.lev_calculator = self.long_dynamic_lev
        else:
            self.lev_calculator = self.long_static_lev

        self.checker_liq_hit = self.long_check_liq_hit

    def long_calc_liq_price(
        self,
        average_entry: float,
        entry_size_usd: float,
        leverage: float,
        og_available_balance: float,
        og_cash_borrowed: float,
        og_cash_used: float,
    ):
        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
        initial_margin = entry_size_usd / leverage
        fee_to_open = entry_size_usd * self.market_fee_pct  # math checked
        possible_bankruptcy_fee = entry_size_usd * (leverage - 1) / leverage * self.mmr_pct
        cash_used = initial_margin + fee_to_open + possible_bankruptcy_fee  # math checked
        logger.debug(
            f"\ninitial_margin= {round(initial_margin, 3)}\
            \nfee_to_open= {round(fee_to_open, 3)}\
            \npossible_bankruptcy_fee= {round(possible_bankruptcy_fee, 3)}\
            \ncash_used= {round(cash_used, 3)}"
        )

        if cash_used > og_available_balance:
            logger.warning("Cash used bigger than available balance")
            raise Exception
        else:
            # liq formula
            # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
            available_balance = round(og_available_balance - cash_used, 3)
            cash_used = round(og_cash_used + cash_used, 3)
            cash_borrowed = round(og_cash_borrowed + entry_size_usd - cash_used, 3)

            liq_price = average_entry * (1 - (1 / leverage) + self.mmr_pct)  # math checked
            liq_price = round_size_by_tick_step(
                user_num=liq_price,
                exchange_num=self.price_tick_step,
            )

        return (
            available_balance,
            cash_borrowed,
            cash_used,
            liq_price,
        )

    def long_static_lev(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        sl_price: float,
    ):
        (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            liq_price,
        ) = self.long_calc_liq_price(
            leverage=self.static_leverage,
            entry_size_usd=entry_size_usd,
            average_entry=average_entry,
            og_cash_used=cash_used,
            og_available_balance=available_balance,
            og_cash_borrowed=cash_borrowed,
        )
        logger.debug(f"Lev set to static lev= {self.static_leverage}")
        return (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            self.static_leverage,
            liq_price,
        )

    def long_dynamic_lev(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        sl_price: float,
    ):
        leverage = -average_entry / ((sl_price - sl_price * 0.001) - average_entry - self.mmr_pct * average_entry)
        leverage = round_size_by_tick_step(
            user_num=leverage,
            exchange_num=self.leverage_tick_step,
        )
        if leverage > self.max_leverage:
            logger.warning(f"Lev too high Lev= {leverage} Max Lev= {self.max_leverage}")
            leverage = self.max_leverage
        elif leverage < self.min_leverage:
            logger.warning(f"Lev too high Lev= {leverage} Max Lev= {self.max_leverage}")
            leverage = 1
        else:
            logger.debug(f"Leverage= {leverage}")

        (
            available_balance,
            cash_borrowed,
            cash_used,
            liq_price,
        ) = self.long_calc_liq_price(
            leverage=leverage,
            entry_size_usd=entry_size_usd,
            average_entry=average_entry,
            og_cash_used=cash_used,
            og_available_balance=available_balance,
            og_cash_borrowed=cash_borrowed,
        )
        return (
            available_balance,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        )

    def long_check_liq_hit(
        self,
        current_candle: np.array,
        liq_price: float,
    ):
        candle_low = current_candle[CandleBodyType.Low]
        logger.debug(f"candle_low= {candle_low}")
        if liq_price > candle_low:
            logger.debug("Liq Hit")
            raise DecreasePosition(
                exit_fee_pct=self.market_fee_pct,
                exit_price=liq_price,
                order_status=OrderStatus.LiquidationFilled,
            )
        else:
            logger.debug("No hit on liq price")
            pass
