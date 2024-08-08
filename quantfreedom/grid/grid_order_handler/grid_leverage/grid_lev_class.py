from logging import getLogger
from typing import Callable
from quantfreedom.helpers.helper_funcs import round_size_by_tick_step
from quantfreedom.core.enums import CurrentFootprintCandleTuple, DecreasePosition, OrderStatus, RejectedOrder

logger = getLogger()


class GridLeverage:

    def calc_liq_price(
        self,
        average_entry: float,
        equity: float,
        get_bankruptcy_price: callable,
        get_liq_price: callable,
        leverage: float,
        market_fee_pct: float,
        mmr_pct: float,
        position_size_asset: float,
        position_size_usd: float,
        price_tick_step: float,
    ):
        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US

        bankruptcy_price = get_bankruptcy_price(
            average_entry=average_entry,
            leverage=leverage,
        )
        initial_margin = position_size_asset * average_entry / leverage
        fee_to_open = position_size_asset * average_entry * market_fee_pct  # math checked
        fee_to_close = position_size_asset * bankruptcy_price * market_fee_pct
        cash_used = round(initial_margin + fee_to_open + fee_to_close, 2)  # math checked

        logger.debug(
            f"""
bankruptcy_price= {round(bankruptcy_price, 2)}
cash_used= {cash_used}
fee to close= {round(fee_to_close, 2)}
fee_to_open= {round(fee_to_open, 2)}
initial_margin= {round(initial_margin, 2)}
"""
        )

        if cash_used > equity:
            logger.warning("Cash used bigger than available balance AKA position size too big")
            raise RejectedOrder
        else:
            available_balance = round(equity - cash_used, 2)
            cash_borrowed = round(position_size_usd - cash_used, 2)

            liq_price = get_liq_price(
                average_entry=average_entry,
                leverage=leverage,
                mmr_pct=mmr_pct,
            )

            rounded_liq_price = round_size_by_tick_step(
                exchange_num=price_tick_step,
                user_num=liq_price,
            )
            logger.debug(
                f"""
available_balance= {available_balance}
cash_borrowed= {cash_borrowed}
"""
            )
        return (
            available_balance,
            cash_borrowed,
            cash_used,
            rounded_liq_price,
        )

    def check_liq_hit(
        self,
        check_liq_hit_bool: callable,
        current_candle: CurrentFootprintCandleTuple,
        liq_price: float,
        market_fee_pct: float,
    ):
        logger.debug(f"liq_price= {liq_price}")

        liq_hit_bool: bool = check_liq_hit_bool(
            current_candle=current_candle,
            liq_price=liq_price,
        )

        if liq_hit_bool:
            logger.debug("Liq Hit")
            raise DecreasePosition(
                exit_fee_pct=market_fee_pct,
                exit_price=liq_price,
                liq_price=liq_price,
                order_status=OrderStatus.LiquidationFilled,
            )
        else:
            logger.debug("No hit on liq price")
            pass
