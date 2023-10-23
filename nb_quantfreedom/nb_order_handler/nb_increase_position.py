from typing import NamedTuple
from nb_quantfreedom.nb_custom_logger import CustomLoggerClass
from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
from numba.experimental import jitclass

from nb_quantfreedom.nb_enums import OrderStatus, RejectedOrder


class AccExOther(NamedTuple):
    account_state_equity: float
    asset_tick_step: float
    logger: CustomLoggerClass
    market_fee_pct: float
    max_asset_size: float
    min_asset_size: float
    possible_loss: float
    price_tick_step: float
    total_trades: int


class OrderInfo(NamedTuple):
    average_entry: float
    entry_price: float
    in_position: float
    max_equity_risk_pct: float
    max_trades: int
    position_size_asset: float
    position_size_usd: float
    risk_account_pct_size: float
    sl_price: float


class IncreasePositionClass:
    def __init__(self) -> None:
        pass

    def calculate_increase_posotion(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        pass

    def calc_in_pos(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        pass

    def calc_not_in_pos(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        pass

    def check_size_too_big_or_small(
        self,
        logger: CustomLoggerClass,
        entry_size_asset: float,
        min_asset_size: float,
        max_asset_size: float,
    ):
        pass

    def pl_risk_account_pct_size(
        self,
        logger: CustomLoggerClass,
        account_state_equity: float,
        possible_loss: float,
        total_trades: int,
        risk_account_pct_size: float,
        max_equity_risk_pct: float,
    ):
        pass

    def tt_amount_based(
        self,
        logger: CustomLoggerClass,
        average_entry: float,
        possible_loss: float,
        position_size_asset: float,
        sl_price: float,
        total_trades: int,
        market_fee_pct: float,
        max_trades: int,
    ):
        pass


@jitclass()
class IncreasePositionNB(IncreasePositionClass):
    def calculate_increase_posotion(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        pass

    def calc_in_pos(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        pass

    def calc_not_in_pos(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        pass

    def check_size_too_big_or_small(
        self,
        logger: CustomLoggerClass,
        entry_size_asset: float,
        min_asset_size: float,
        max_asset_size: float,
    ):
        pass

    def pl_risk_account_pct_size(
        self,
        logger: CustomLoggerClass,
        account_state_equity: float,
        possible_loss: float,
        total_trades: int,
        risk_account_pct_size: float,
        max_equity_risk_pct: float,
    ):
        pass

    def tt_amount_based(
        self,
        logger: CustomLoggerClass,
        average_entry: float,
        possible_loss: float,
        position_size_asset: float,
        sl_price: float,
        total_trades: int,
        market_fee_pct: float,
        max_trades: int,
    ):
        pass


@jitclass()
class nb_IPHelpers(IncreasePositionClass):
    def check_size_too_big_or_small(
        self,
        logger: CustomLoggerClass,
        entry_size_asset: float,
        min_asset_size: float,
        max_asset_size: float,
    ):
        if entry_size_asset < min_asset_size:
            logger.log_warning(
                "nb_increase_position.py - nb_IPHelpers - check_size_too_big_or_small() - entry size too small "
                + "entry_size_asset= "
                + logger.float_to_str(entry_size_asset)
                + " < min_asset_size= "
                + logger.float_to_str(min_asset_size)
            )
            raise RejectedOrder
        elif entry_size_asset > max_asset_size:
            logger.log_warning(
                "nb_increase_position.py - nb_IPHelpers - check_size_too_big_or_small() - entry size too big"
                + "entry_size_asset= "
                + logger.float_to_str(entry_size_asset)
                + " > max_asset_size= "
                + logger.float_to_str(max_asset_size)
            )
            raise RejectedOrder

        logger.log_debug(
            "nb_increase_position.py - nb_IPHelpers - check_size_too_big_or_small() - Entry size is fine"
            + "entry_size_asset= "
            + logger.float_to_str(entry_size_asset)
        )

    def pl_risk_account_pct_size(
        self,
        logger: CustomLoggerClass,
        account_state_equity: float,
        possible_loss: float,
        total_trades: int,
        risk_account_pct_size: float,
        max_equity_risk_pct: float,
    ):
        logger.log_debug("nb_increase_position.py - nb_IPHelpers - pl_risk_account_pct_size() - Inside")
        possible_loss = round(possible_loss + account_state_equity * risk_account_pct_size, 0)
        logger.log_debug(
            "nb_increase_position.py - nb_IPHelpers - pl_risk_account_pct_size() -"
            + " possible_loss= "
            + str(int(possible_loss))
        )
        max_equity_risk = round(account_state_equity * max_equity_risk_pct)
        logger.log_debug(
            "nb_increase_position.py - nb_IPHelpers - pl_risk_account_pct_size() -"
            + " max_equity_risk= "
            + str(int(max_equity_risk))
        )
        if possible_loss > max_equity_risk:
            logger.log_warning(
                "nb_increase_position.py - nb_IPHelpers - pl_risk_account_pct_size() - Too big"
                + " possible_loss= "
                + str(int(possible_loss))
                + " max risk= "
                + str(int(max_equity_risk))
            )
            raise RejectedOrder
        total_trades += 1
        logger.log_debug(
            "nb_increase_position.py - nb_IPHelpers - pl_risk_account_pct_size() - PL is fine"
            + " possible_loss= "
            + str(int(possible_loss))
            + " max risk= "
            + str(int(max_equity_risk))
            + " total trades= "
            + str(int(total_trades))
        )
        return possible_loss, total_trades

    def tt_amount_based(
        self,
        logger: CustomLoggerClass,
        average_entry: float,
        possible_loss: float,
        position_size_asset: float,
        sl_price: float,
        total_trades: int,
        market_fee_pct: float,
        max_trades: int,
    ):
        pnl = position_size_asset * (sl_price - average_entry)  # math checked
        fee_open = position_size_asset * average_entry * market_fee_pct  # math checked
        fee_close = position_size_asset * sl_price * market_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        possible_loss = round(-(pnl - fees_paid), 3)
        logger.log_debug(
            "nb_increase_position.py - nb_IPHelpers - tt_amount_based() -"
            + " possible_loss= "
            + str(int(possible_loss))
        )
        total_trades += 1
        if total_trades > max_trades:
            logger.log_warning(
                "nb_increase_position.py - nb_IPHelpers - tt_amount_based() - Max trades reached"
                + " total trades= "
                + str(int(total_trades))
                + " max trades= "
                + str(int(max_trades))
                + " possible_loss= "
                + logger.float_to_str(possible_loss)
            )
            raise RejectedOrder
        logger.log_debug(
            "nb_increase_position.py - nb_IPHelpers - tt_amount_based() - Max trades reached "
            + "total trades= "
            + str(int(total_trades))
            + " max trades= "
            + str(int(max_trades))
            + " possible_loss= "
            + logger.float_to_str(possible_loss)
        )
        return possible_loss, total_trades


@jitclass()
class nb_Long_RPAandSLB:
    """
    Risking percent of your account while also having your stop loss based open high low or close of a candle
    """

    def __init__(self) -> None:
        pass

    def calculate_increase_posotion(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        if order_info.in_position:
            acc_ex_other.logger.log_debug(
                "nb_increase_position.py - nb_Long_RPAandSLB - calculate_increase_posotion() - We are in a position"
            )
            return self.calc_in_pos(acc_ex_other=acc_ex_other, order_info=order_info)
        else:
            acc_ex_other.logger.log_debug(
                "nb_increase_position.py - nb_Long_RPAandSLB - calculate_increase_posotion() - Not in a position"
            )
            return self.calc_not_in_pos(acc_ex_other=acc_ex_other, order_info=order_info)

    def calc_in_pos(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        account_state_equity = acc_ex_other.account_state_equity
        asset_tick_step = acc_ex_other.asset_tick_step
        logger = acc_ex_other.logger
        market_fee_pct = acc_ex_other.market_fee_pct
        max_asset_size = acc_ex_other.max_asset_size
        min_asset_size = acc_ex_other.min_asset_size
        possible_loss = acc_ex_other.possible_loss
        price_tick_step = acc_ex_other.price_tick_step
        total_trades = acc_ex_other.total_trades

        average_entry = order_info.average_entry
        entry_price = order_info.entry_price
        max_equity_risk_pct = order_info.max_equity_risk_pct
        position_size_asset = order_info.position_size_asset
        position_size_usd = order_info.position_size_usd
        risk_account_pct_size = order_info.risk_account_pct_size
        sl_price = order_info.sl_price

        logger.log_debug("nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - Calculating")
        possible_loss, total_trades = nb_IPHelpers().pl_risk_account_pct_size(
            logger=logger,
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
            total_trades=total_trades,
            risk_account_pct_size=risk_account_pct_size,
            max_equity_risk_pct=max_equity_risk_pct,
        )

        entry_size_usd = round(
            -(
                (
                    -possible_loss * entry_price * average_entry
                    + entry_price * position_size_usd * average_entry
                    - sl_price * entry_price * position_size_usd
                    + sl_price * entry_price * position_size_usd * market_fee_pct
                    + entry_price * position_size_usd * average_entry * market_fee_pct
                )
                / (average_entry * (entry_price - sl_price + entry_price * market_fee_pct + sl_price * market_fee_pct))
            ),
            3,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - "
            + "entry_size_usd= "
            + logger.float_to_str(entry_size_usd)
        )

        entry_size_asset = nb_round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=asset_tick_step,
        )
        self.check_size_too_big_or_small(
            logger=logger,
            entry_size_asset=entry_size_asset,
            min_asset_size=min_asset_size,
            max_asset_size=max_asset_size,
        )

        position_size_asset = nb_round_size_by_tick_step(
            user_num=position_size_asset + entry_size_asset,
            exchange_num=asset_tick_step,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - "
            + "position_size_asset= "
            + logger.float_to_str(position_size_asset)
        )

        position_size_usd = round(entry_size_usd + position_size_usd, 3)
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - "
            + "position_size_usd= "
            + logger.float_to_str(position_size_usd)
        )

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = nb_round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=price_tick_step,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - "
            + "average_entry= "
            + logger.float_to_str(average_entry)
        )

        sl_pct = round((average_entry - sl_price) / average_entry, 3)
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - "
            + "sl_pct= "
            + logger.float_to_str(round(sl_pct * 100, 3))
        )

        logger.log_info(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - "
            + "\naverage_entry= "
            + logger.float_to_str(average_entry)
            + "\nentry_price= "
            + logger.float_to_str(entry_price)
            + "\nentry_size_asset= "
            + logger.float_to_str(entry_size_asset)
            + "\nentry_size_usd= "
            + logger.float_to_str(entry_size_usd)
            + "\nposition_size_asset= "
            + logger.float_to_str(position_size_asset)
            + "\nposition_size_usd= "
            + logger.float_to_str(position_size_usd)
            + "\npossible_loss= "
            + logger.float_to_str(possible_loss)
            + "\ntotal_trades= "
            + logger.float_to_str(total_trades)
            + "\nsl_pct= "
            + logger.float_to_str(round(sl_pct * 100, 3))
        )
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            possible_loss,
            total_trades,
            sl_pct,
        )

    def calc_not_in_pos(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        account_state_equity = acc_ex_other.account_state_equity
        asset_tick_step = acc_ex_other.asset_tick_step
        logger = acc_ex_other.logger
        market_fee_pct = acc_ex_other.market_fee_pct
        max_asset_size = acc_ex_other.max_asset_size
        min_asset_size = acc_ex_other.min_asset_size
        possible_loss = acc_ex_other.possible_loss
        total_trades = acc_ex_other.total_trades

        average_entry = order_info.average_entry
        entry_price = order_info.entry_price
        max_equity_risk_pct = order_info.max_equity_risk_pct
        position_size_asset = order_info.position_size_asset
        position_size_usd = order_info.position_size_usd
        risk_account_pct_size = order_info.risk_account_pct_size
        sl_price = order_info.sl_price

        logger.log_debug("nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - Calculating")
        possible_loss, total_trades = nb_IPHelpers().pl_risk_account_pct_size(
            logger=logger,
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
            total_trades=total_trades,
            risk_account_pct_size=risk_account_pct_size,
            max_equity_risk_pct=max_equity_risk_pct,
        )

        entry_size_usd = position_size_usd = round(
            -possible_loss / (sl_price / entry_price - 1 - market_fee_pct - sl_price * market_fee_pct / entry_price),
            3,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - "
            + "entry_size_usd= "
            + logger.float_to_str(entry_size_usd)
        )
        entry_size_asset = position_size_asset = nb_round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=asset_tick_step,
        )
        self.check_size_too_big_or_small(
            logger=logger,
            entry_size_asset=entry_size_asset,
            min_asset_size=min_asset_size,
            max_asset_size=max_asset_size,
        )

        average_entry = entry_price

        sl_pct = round((average_entry - sl_price) / average_entry, 3)
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - "
            + "sl_pct= "
            + logger.float_to_str(round(sl_pct * 100, 3))
        )

        logger.log_info(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - "
            + "\naverage_entry= "
            + logger.float_to_str(average_entry)
            + "\nentry_price= "
            + logger.float_to_str(entry_price)
            + "\nentry_size_asset= "
            + logger.float_to_str(entry_size_asset)
            + "\nentry_size_usd= "
            + logger.float_to_str(entry_size_usd)
            + "\nposition_size_asset= "
            + logger.float_to_str(position_size_asset)
            + "\nposition_size_usd= "
            + logger.float_to_str(position_size_usd)
            + "\npossible_loss= "
            + logger.float_to_str(possible_loss)
            + "\ntotal_trades= "
            + logger.float_to_str(total_trades)
            + "\nsl_pct= "
            + logger.float_to_str(round(sl_pct * 100, 3))
        )
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            possible_loss,
            total_trades,
            sl_pct,
        )


@jitclass()
class nb_Long_SEP:
    """
    Setting your position size to the min amount the exchange will allow

    """

    def __init__(self) -> None:
        pass

    def calculate_increase_posotion(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        if order_info.in_position:
            acc_ex_other.logger.log_debug(
                "nb_increase_position.py - nb_Long_RPAandSLB - calculate_increase_posotion() - We are in a position"
            )
            return self.calc_in_pos(
                acc_ex_other=acc_ex_other,
                order_info=order_info,
            )
        else:
            acc_ex_other.logger.log_debug(
                "nb_increase_position.py - nb_Long_RPAandSLB - calculate_increase_posotion() - Not in a position"
            )
            return self.calc_not_in_pos(
                acc_ex_other=acc_ex_other,
                order_info=order_info,
            )

    def calc_in_pos(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        logger = acc_ex_other.logger
        market_fee_pct = acc_ex_other.market_fee_pct
        max_asset_size = acc_ex_other.max_asset_size
        min_asset_size = acc_ex_other.min_asset_size
        possible_loss = acc_ex_other.possible_loss
        price_tick_step = acc_ex_other.price_tick_step
        total_trades = acc_ex_other.total_trades

        average_entry = order_info.average_entry
        entry_price = order_info.entry_price
        max_trades = order_info.max_trades
        position_size_asset = order_info.position_size_asset
        position_size_usd = order_info.position_size_usd
        sl_price = order_info.sl_price

        logger.log_debug("nb_increase_position.py - Calculating")

        position_size_asset += min_asset_size
        entry_size_asset = min_asset_size
        logger.log_debug("entry_size_asset position_size_asset{entry_size_asset, position_size_asset}")

        entry_size_usd = round(min_asset_size * entry_price, 3)
        logger.log_debug("entry_size_usd entry_size_usd}")

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = nb_round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=price_tick_step,
        )
        logger.log_debug("average_entry average_entry}")

        sl_pct = round((average_entry - sl_price) / average_entry, 3)
        logger.log_debug("sl_pct={round(sl_pct*100,2))")

        position_size_usd = round(entry_size_usd + position_size_usd, 3)
        logger.log_debug("position_size_usd position_size_usd}")

        possible_loss, total_trades = nb_IPHelpers().tt_amount_based(
            average_entry=average_entry,
            possible_loss=possible_loss,
            total_trades=total_trades,
            position_size_asset=position_size_asset,
            sl_price=sl_price,
            market_fee_pct=market_fee_pct,
            max_trades=max_trades,
        )
        logger.log_debug("possible_loss, total_trades {possible_loss, total_trades}")

        self.check_size_too_big_or_small(
            logger=logger,
            entry_size_asset=entry_size_asset,
            min_asset_size=min_asset_size,
            max_asset_size=max_asset_size,
        )
        logger.log_info(
            "\n\
average_entry= average_entry)\n\
entry_price= entry_price)\n\
entry_size_asset= entry_size_asset)\n\
entry_size_usd= entry_size_usd)\n\
position_size_asset= position_size_asset)\n\
position_size_usd= position_size_usd)\n\
possible_loss= possible_loss)\n\
total_trades=total_trades)\n\
sl_pct= {round(sl_pct*100,2))"
        )
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            possible_loss,
            total_trades,
            sl_pct,
        )

    def calc_not_in_pos(self, acc_ex_other: AccExOther, order_info: OrderInfo):
        logger = acc_ex_other.logger
        market_fee_pct = acc_ex_other.market_fee_pct
        max_asset_size = acc_ex_other.max_asset_size
        min_asset_size = acc_ex_other.min_asset_size
        possible_loss = acc_ex_other.possible_loss
        total_trades = acc_ex_other.total_trades

        average_entry = order_info.average_entry
        entry_price = order_info.entry_price
        max_trades = order_info.max_trades
        position_size_asset = order_info.position_size_asset
        position_size_usd = order_info.position_size_usd
        sl_price = order_info.sl_price

        logger.log_debug("nb_increase_position.py - Calculating")
        entry_size_asset = position_size_asset = min_asset_size
        logger.log_debug("entry_size_asset position_size_asset{entry_size_asset, position_size_asset}")

        entry_size_usd = position_size_usd = round(entry_size_asset * entry_price, 3)
        logger.log_debug("entry_size_usd position_size_usd {entry_size_usd, position_size_usd}")

        average_entry = entry_price
        logger.log_debug("average_entry average_entry}")
        sl_pct = round((average_entry - sl_price) / average_entry, 3)
        logger.log_debug("sl_pct={round(sl_pct*100,2))")

        possible_loss, total_trades = nb_IPHelpers().tt_amount_based(
            average_entry=average_entry,
            possible_loss=possible_loss,
            total_trades=total_trades,
            position_size_asset=position_size_asset,
            sl_price=sl_price,
            market_fee_pct=market_fee_pct,
            max_trades=max_trades,
        )
        logger.log_debug("possible_loss, total_trades {possible_loss, total_trades}")

        self.check_size_too_big_or_small(
            logger=logger,
            entry_size_asset=entry_size_asset,
            min_asset_size=min_asset_size,
            max_asset_size=max_asset_size,
        )
        logger.log_info(
            "\n\
average_entry= average_entry)\n\
entry_price= entry_price)\n\
entry_size_asset= entry_size_asset)\n\
entry_size_usd= entry_size_usd)\n\
position_size_asset= position_size_asset)\n\
position_size_usd= position_size_usd)\n\
possible_loss= possible_loss)\n\
total_trades=total_trades)\n\
sl_pct= {round(sl_pct*100,2))"
        )
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            possible_loss,
            total_trades,
            sl_pct,
        )
