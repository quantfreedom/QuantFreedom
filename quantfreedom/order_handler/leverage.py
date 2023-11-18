import numpy as np
from logging import getLogger
from quantfreedom.enums import CandleBodyType, DecreasePosition, LeverageStrategyType, OrderStatus, RejectedOrder
from quantfreedom.helper_funcs import round_size_by_tick_step

logger = getLogger("info")


class Leverage:
    def __init__(
        self,
        leverage_strategy_type: LeverageStrategyType,
        leverage_tick_step: float,
        market_fee_pct: float,
        max_leverage: float,
        min_leverage: float,
        mmr_pct: float,
        price_tick_step: float,
        static_leverage: float,
        long_short: str,
    ):
        self.min_leverage = min_leverage
        self.price_tick_step = price_tick_step
        self.leverage_tick_step = leverage_tick_step
        self.max_leverage = max_leverage
        self.mmr_pct = mmr_pct
        self.market_fee_pct = market_fee_pct
        self.static_leverage = static_leverage

        if long_short == "long":
            self.calc_dynamic_lev = self.long_calc_dynamic_lev
            self.get_liq_price = self.long_get_liq_price
            self.get_bankruptcy_price = self.long_get_bankruptcy_price
            self.liq_hit_bool = self.long_liq_hit_bool
        else:
            self.calc_dynamic_lev = self.short_calc_dynamic_lev
            self.get_liq_price = self.short_get_liq_price
            self.get_bankruptcy_price = self.short_get_bankruptcy_price
            self.liq_hit_bool = self.short_liq_hit_bool

        if leverage_strategy_type == LeverageStrategyType.Dynamic:
            self.lev_calculator = self.dynamic_lev
        else:
            self.lev_calculator = self.calc_liq_price

        self.checker_liq_hit = self.check_liq_hit

    def long_get_bankruptcy_price(
        self,
        average_entry: float,
        leverage: float,
    ):
        # https://www.bybithelp.com/en-US/s/article/Order-Cost-USDT-Contract
        return average_entry * (leverage - 1) / leverage

    def short_get_bankruptcy_price(
        self,
        average_entry: float,
        leverage: float,
    ):
        # https://www.bybithelp.com/en-US/s/article/Order-Cost-USDT-Contract
        return average_entry * (leverage + 1) / leverage

    def long_get_liq_price(
        self,
        average_entry: float,
        leverage: float,
    ):
        # liq formula
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
        return average_entry * (1 - (1 / leverage) + self.mmr_pct)

    def short_get_liq_price(
        self,
        average_entry: float,
        leverage: float,
    ):
        # liq formula
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
        return average_entry * (1 + (1 / leverage) - self.mmr_pct)

    def calc_liq_price(
        self,
        average_entry: float,
        leverage: float,
        og_available_balance: float,
        og_cash_borrowed: float,
        og_cash_used: float,
        position_size_asset: float,
        position_size_usd: float,
    ):
        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US

        initial_margin = (position_size_asset * average_entry) / leverage
        fee_to_open = position_size_asset * average_entry * self.market_fee_pct  # math checked
        bankruptcy_price = self.get_bankruptcy_price(average_entry=average_entry, leverage=leverage)
        fee_to_close = position_size_asset * bankruptcy_price * self.market_fee_pct

        cash_used = initial_margin + fee_to_open + fee_to_close  # math checked

        logger.debug(
            f"\ninitial_margin= {round(initial_margin, 3)}\
            \nfee_to_open= {round(fee_to_open, 3)}\
            \nbankruptcy_price= {round(bankruptcy_price, 3)}\
            \nfee to close= {round(fee_to_close, 3)}\
            \ncash_used= {round(cash_used, 3)}\
            \nog_available_balance= {og_available_balance}"
        )

        if cash_used > og_available_balance:
            logger.warning("Cash used bigger than available balance AKA position size too big")
            raise RejectedOrder
        else:
            available_balance = round(og_available_balance - cash_used, 3)
            cash_used = round(og_cash_used + cash_used, 3)
            cash_borrowed = round(og_cash_borrowed + position_size_usd - cash_used, 3)

            liq_price = self.get_liq_price(average_entry=average_entry, leverage=leverage)  # math checked
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

    def static_lev(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        position_size_asset: float,
        position_size_usd: float,
        sl_price: float,
    ):
        (
            available_balance,
            can_move_sl_to_be,
            cash_borrowed,
            cash_used,
            liq_price,
        ) = self.calc_liq_price(
            leverage=self.static_leverage,
            position_size_asset=position_size_asset,
            position_size_usd=position_size_usd,
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

    def long_calc_dynamic_lev(
        self,
        average_entry: float,
        sl_price: float,
    ):
        # the .001 is to add .001 buffer
        return -average_entry / ((sl_price - sl_price * 0.001) - average_entry - (self.mmr_pct * average_entry))

    def short_calc_dynamic_lev(
        self,
        average_entry: float,
        sl_price: float,
    ):
        # the .001 is to add .001 buffer
        return average_entry / ((sl_price + sl_price * 0.001) - average_entry + (self.mmr_pct * average_entry))

    def dynamic_lev(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        position_size_asset: float,
        position_size_usd: float,
        sl_price: float,
    ):
        leverage = self.calc_dynamic_lev(average_entry=average_entry, sl_price=sl_price)
        leverage = round_size_by_tick_step(
            user_num=leverage,
            exchange_num=self.leverage_tick_step,
        )
        if leverage > self.max_leverage:
            logger.warning(f"Lev too high Lev= {leverage} Max Lev= {self.max_leverage}")
            leverage = self.max_leverage
        elif leverage < self.min_leverage:
            logger.warning(f"Lev too low Lev= {leverage} Min Lev= {self.min_leverage}")
            leverage = 1
        else:
            logger.debug(f"Leverage= {leverage}")

        (
            available_balance,
            cash_borrowed,
            cash_used,
            liq_price,
        ) = self.calc_liq_price(
            leverage=leverage,
            average_entry=average_entry,
            og_cash_used=cash_used,
            og_available_balance=available_balance,
            og_cash_borrowed=cash_borrowed,
            position_size_asset=position_size_asset,
            position_size_usd=position_size_usd,
        )
        return (
            available_balance,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        )

    def long_liq_hit_bool(
        self,
        current_candle: np.array,
        liq_price: float,
    ):
        candle_low = current_candle[CandleBodyType.Low]
        logger.debug(f"candle_low= {candle_low}")
        return liq_price > candle_low

    def short_liq_hit_bool(
        self,
        current_candle: np.array,
        liq_price: float,
    ):
        candle_high = current_candle[CandleBodyType.High]
        logger.debug(f"candle_high= {candle_high}")
        return liq_price < candle_high

    def check_liq_hit(
        self,
        current_candle: np.array,
        liq_price: float,
    ):
        if self.liq_hit_bool(current_candle=current_candle, liq_price=liq_price):
            logger.debug("Liq Hit")
            raise DecreasePosition(
                exit_fee_pct=self.market_fee_pct,
                exit_price=liq_price,
                order_status=OrderStatus.LiquidationFilled,
            )
        else:
            logger.debug("No hit on liq price")
            pass
