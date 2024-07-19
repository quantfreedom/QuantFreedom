from logging import getLogger
from quantfreedom.helpers.helper_funcs import round_size_by_tick_step
from quantfreedom.core.enums import CurrentFootprintCandleTuple, DecreasePosition, OrderStatus, RejectedOrder

logger = getLogger()


class GridLeverage:

    def calc_liq_price(
        self,
        average_entry: float,
        get_bankruptcy_price_exec: str,
        get_liq_price_exec: str,
        leverage: float,
        market_fee_pct: float,
        mmr_pct: float,
        og_available_balance: float,
        og_cash_borrowed: float,
        og_cash_used: float,
        position_size_asset: float,
        position_size_usd: float,
        price_tick_step: float,
    ):
        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US

        bankruptcy_price: float
        liq_price: float

        initial_margin = (position_size_asset * average_entry) / leverage
        fee_to_open = position_size_asset * average_entry * market_fee_pct  # math checked

        exec(get_bankruptcy_price_exec)  # gets bankruptcy price

        fee_to_close = position_size_asset * bankruptcy_price * market_fee_pct

        cash_used = initial_margin + fee_to_open + fee_to_close  # math checked

        logger.debug(
            f"""
initial_margin= {round(initial_margin, 2)}
fee_to_open= {round(fee_to_open, 2)}
bankruptcy_price= {round(bankruptcy_price, 2)}
fee to close= {round(fee_to_close, 2)}
cash_used= {round(cash_used, 2)}
og_available_balance= {og_available_balance}"""
        )

        if cash_used > og_available_balance:
            msg = "Cash used bigger than available balance AKA position size too big"
            logger.warning(msg)
            raise RejectedOrder
        else:
            available_balance = round(og_available_balance - cash_used, 2)
            cash_used = round(og_cash_used + cash_used, 2)
            cash_borrowed = round(og_cash_borrowed + position_size_usd - cash_used, 2)

            exec(get_liq_price_exec)  # gets liq price

            rounded_liq_price = round_size_by_tick_step(
                user_num=liq_price,
                exchange_num=price_tick_step,
            )

        return (
            available_balance,
            cash_borrowed,
            cash_used,
            rounded_liq_price,
        )

    def check_liq_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        liq_price: float,
        liq_hit_bool_exec: str,
        market_fee_pct: float,
    ):
        liq_hit_bool: bool
        exec(liq_hit_bool_exec)  # checks if liq was hit

        if liq_hit_bool:
            logger.debug("Liq Hit")
            raise DecreasePosition(
                exit_fee_pct=market_fee_pct,
                liq_price=liq_price,
                order_status=OrderStatus.LiquidationFilled,
            )
        else:
            logger.debug("No hit on liq price")
            pass
