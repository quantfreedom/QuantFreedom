from nb_quantfreedom.nb_custom_logger import CustomLoggerNB
from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
from numba.experimental import jitclass

from nb_quantfreedom.nb_enums import OrderStatus, RejectedOrder


class IncreasePositionClass:
    def __init__(self) -> None:
        pass

    def calculate_increase_posotion(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        in_position: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        pass

    def calc_in_pos(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        pass

    def calc_not_in_pos(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        pass

    def check_size_too_big_or_small(
        self,
        logger: CustomLoggerNB,
        entry_size_asset: float,
        min_asset_size: float,
        max_asset_size: float,
    ):
        pass

    def pl_risk_account_pct_size(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        possible_loss: float,
        total_trades: int,
        risk_account_pct_size: float,
        max_equity_risk_pct: float,
    ):
        pass

    def tt_amount_based(
        self,
        logger: CustomLoggerNB,
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
    def calculate_increase_posotion(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        in_position: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        pass

    def calc_in_pos(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        pass

    def calc_not_in_pos(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        pass

    def check_size_too_big_or_small(
        self,
        logger: CustomLoggerNB,
        entry_size_asset: float,
        min_asset_size: float,
        max_asset_size: float,
    ):
        pass

    def pl_risk_account_pct_size(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        possible_loss: float,
        total_trades: int,
        risk_account_pct_size: float,
        max_equity_risk_pct: float,
    ):
        pass

    def tt_amount_based(
        self,
        logger: CustomLoggerNB,
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
class nb_IPHelpers(IncreasePositionNB):
    def check_size_too_big_or_small(
        self,
        logger: CustomLoggerNB,
        entry_size_asset: float,
        min_asset_size: float,
        max_asset_size: float,
    ):
        if entry_size_asset < min_asset_size:
            raise RejectedOrder(
                msg="Entry Size too small entry_size_asset} min_asset_size=min_asset_size}",
                order_status=OrderStatus.EntrySizeTooSmall,
            )

        elif entry_size_asset > max_asset_size:
            raise RejectedOrder(
                msg="Entry Size too big entry_size_asset} max asset size=max_asset_size}",
                order_status=OrderStatus.EntrySizeTooBig,
            )

        logger.log_debug("Entry size is fine")

    def pl_risk_account_pct_size(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        possible_loss: float,
        total_trades: int,
        risk_account_pct_size: float,
        max_equity_risk_pct: float,
    ):
        possible_loss = round(possible_loss + account_state_equity * risk_account_pct_size)
        max_equity_risk = round(account_state_equity * max_equity_risk_pct)
        if possible_loss > max_equity_risk:
            raise RejectedOrder(
                msg="PL too big possible_loss} max risk=max_equity_risk}",
                order_status=OrderStatus.PossibleLossTooBig,
                at_max_entries=True,
            )
        total_trades += 1
        logger.log_debug("Possible Loss is fine")
        return possible_loss, total_trades

    def tt_amount_based(
        self,
        logger: CustomLoggerNB,
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
        possible_loss = round(-(pnl - fees_paid), 4)

        total_trades += 1
        if total_trades > max_trades:
            raise RejectedOrder(
                msg="Max Trades to big total_trades} mt=max_trades}",
                order_status=OrderStatus.HitMaxTrades,
                at_max_entries=True,
            )
        logger.log_debug("total trades is fine")
        return possible_loss, total_trades


@jitclass()
class nb_Long_RPAandSLB(IncreasePositionNB):
    """
    Risking percent of your account while also having your stop loss based open high low or close of a candle
    """

    def calculate_increase_posotion(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        in_position: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        if in_position:
            logger.log_debug(
                "nb_increase_position.py - nb_Long_RPAandSLB - calculate_increase_posotion() - We are in a position"
            )
            return self.calc_in_pos(
                account_state_equity=account_state_equity,
                asset_tick_step=asset_tick_step,
                average_entry=average_entry,
                entry_price=entry_price,
                market_fee_pct=market_fee_pct,
                max_asset_size=max_asset_size,
                max_equity_risk_pct=max_equity_risk_pct,
                max_trades=max_trades,
                min_asset_size=min_asset_size,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
                possible_loss=possible_loss,
                price_tick_step=price_tick_step,
                risk_account_pct_size=risk_account_pct_size,
                sl_price=sl_price,
                total_trades=total_trades,
                logger=logger,
            )
        else:
            logger.log_debug(
                "nb_increase_position.py - nb_Long_RPAandSLB - calculate_increase_posotion() - Not in a position"
            )
            return self.calc_not_in_pos(
                account_state_equity=account_state_equity,
                asset_tick_step=asset_tick_step,
                average_entry=average_entry,
                entry_price=entry_price,
                market_fee_pct=market_fee_pct,
                max_asset_size=max_asset_size,
                max_equity_risk_pct=max_equity_risk_pct,
                max_trades=max_trades,
                min_asset_size=min_asset_size,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
                possible_loss=possible_loss,
                price_tick_step=price_tick_step,
                risk_account_pct_size=risk_account_pct_size,
                sl_price=sl_price,
                total_trades=total_trades,
                logger=logger,
            )

    def calc_in_pos(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        # need to put in checks to make sure the size isn't too big or goes over or something
        logger.log_debug("nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - Calculating")
        possible_loss, total_trades = nb_IPHelpers().pl_risk_account_pct_size(
            logger=logger,
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
            total_trades=total_trades,
            risk_account_pct_size=risk_account_pct_size,
            max_equity_risk_pct=max_equity_risk_pct,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - possible_loss, total_trades {possible_loss, total_trades}"
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
            4,
        )
        logger.log_debug("nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - entry_size_usd entry_size_usd}")

        position_size_usd = round(entry_size_usd + position_size_usd, 4)
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - position_size_usd = osition_size_usd}"
        )

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = nb_round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=price_tick_step,
        )
        logger.log_debug("nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - average_entry average_entry}")

        sl_pct = round((average_entry - sl_price) / average_entry, 4)
        logger.log_debug("nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - sl_pct={round(sl_pct*100,2):,}")

        entry_size_asset = nb_round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=asset_tick_step,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - entry_size_asset entry_size_asset}"
        )

        position_size_asset = nb_round_size_by_tick_step(
            user_num=position_size_asset + entry_size_asset,
            exchange_num=asset_tick_step,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - position_size_asset position_size_asset}"
        )

        self.check_size_too_big_or_small(
            logger=logger,
            entry_size_asset=entry_size_asset,
            min_asset_size=min_asset_size,
            max_asset_size=max_asset_size,
        )
        logger.log_info(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_in_pos() - \n\
average_entry= average_entry:,}\n\
entry_price= entry_price:,}\n\
entry_size_asset= entry_size_asset:,}\n\
entry_size_usd= entry_size_usd:,}\n\
position_size_asset= position_size_asset:,}\n\
position_size_usd= position_size_usd:,}\n\
possible_loss= possible_loss:,}\n\
total_trades= total_trades:,}\n\
sl_pct= {round(sl_pct*100,2):,}"
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

    def calc_not_in_pos(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        logger.log_debug("nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - Calculating")
        possible_loss, total_trades = nb_IPHelpers().pl_risk_account_pct_size(
            logger=logger,
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
            total_trades=total_trades,
            risk_account_pct_size=risk_account_pct_size,
            max_equity_risk_pct=max_equity_risk_pct,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - possible_loss, total_trades {possible_loss, total_trades}"
        )

        entry_size_usd = position_size_usd = round(
            -possible_loss / (sl_price / entry_price - 1 - market_fee_pct - sl_price * market_fee_pct / entry_price),
            4,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - entry_size_usd position_size_usd {entry_size_usd, position_size_usd}"
        )

        average_entry = entry_price
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - average_entry average_entry}"
        )

        sl_pct = round((average_entry - sl_price) / average_entry, 4)
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - sl_pct={round(sl_pct*100,2):,}"
        )

        entry_size_asset = position_size_asset = nb_round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=asset_tick_step,
        )
        logger.log_debug(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - entry_size_asset position_size_asset{entry_size_asset, position_size_asset}"
        )

        self.check_size_too_big_or_small(
            logger=logger,
            entry_size_asset=entry_size_asset,
            min_asset_size=min_asset_size,
            max_asset_size=max_asset_size,
        )
        logger.log_info(
            "nb_increase_position.py - nb_Long_RPAandSLB - calc_not_in_pos() - \n\
average_entry= average_entry:,}\n\
entry_price= entry_price:,}\n\
entry_size_asset= entry_size_asset:,}\n\
entry_size_usd= entry_size_usd:,}\n\
position_size_asset= position_size_asset:,}\n\
position_size_usd= position_size_usd:,}\n\
possible_loss= possible_loss:,}\n\
total_trades=total_trades:,}\n\
sl_pct= {round(sl_pct*100,2):,}"
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
class nb_Long_SEP(IncreasePositionNB):
    """
    Setting your position size to the min amount the exchange will allow

    """

    def calculate_increase_posotion(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        in_position: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        if in_position:
            logger.log_debug("nb_increase_position.py - We are in a position")
            return self.calc_in_pos(
                account_state_equity=account_state_equity,
                asset_tick_step=asset_tick_step,
                average_entry=average_entry,
                entry_price=entry_price,
                market_fee_pct=market_fee_pct,
                max_asset_size=max_asset_size,
                max_equity_risk_pct=max_equity_risk_pct,
                max_trades=max_trades,
                min_asset_size=min_asset_size,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
                possible_loss=possible_loss,
                price_tick_step=price_tick_step,
                risk_account_pct_size=risk_account_pct_size,
                sl_price=sl_price,
                total_trades=total_trades,
            )
        else:
            logger.log_debug("nb_increase_position.py - Not in a position")
            return self.calc_not_in_pos(
                account_state_equity=account_state_equity,
                asset_tick_step=asset_tick_step,
                average_entry=average_entry,
                entry_price=entry_price,
                market_fee_pct=market_fee_pct,
                max_asset_size=max_asset_size,
                max_equity_risk_pct=max_equity_risk_pct,
                max_trades=max_trades,
                min_asset_size=min_asset_size,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
                possible_loss=possible_loss,
                price_tick_step=price_tick_step,
                risk_account_pct_size=risk_account_pct_size,
                sl_price=sl_price,
                total_trades=total_trades,
            )

    def calc_in_pos(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        # need to put in checks to make sure the size isn't too big or goes over or something
        logger.log_debug("nb_increase_position.py - Calculating")

        position_size_asset += min_asset_size
        entry_size_asset = min_asset_size
        logger.log_debug("entry_size_asset position_size_asset{entry_size_asset, position_size_asset}")

        entry_size_usd = round(min_asset_size * entry_price, 4)
        logger.log_debug("entry_size_usd entry_size_usd}")

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = nb_round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=price_tick_step,
        )
        logger.log_debug("average_entry average_entry}")

        sl_pct = round((average_entry - sl_price) / average_entry, 4)
        logger.log_debug("sl_pct={round(sl_pct*100,2):,}")

        position_size_usd = round(entry_size_usd + position_size_usd, 4)
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
average_entry= average_entry:,}\n\
entry_price= entry_price:,}\n\
entry_size_asset= entry_size_asset:,}\n\
entry_size_usd= entry_size_usd:,}\n\
position_size_asset= position_size_asset:,}\n\
position_size_usd= position_size_usd:,}\n\
possible_loss= possible_loss:,}\n\
total_trades=total_trades:,}\n\
sl_pct= {round(sl_pct*100,2):,}"
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

    def calc_not_in_pos(
        self,
        logger: CustomLoggerNB,
        account_state_equity: float,
        asset_tick_step: float,
        average_entry: float,
        entry_price: float,
        market_fee_pct: float,
        max_asset_size: float,
        max_equity_risk_pct: float,
        max_trades: int,
        min_asset_size: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        price_tick_step: float,
        risk_account_pct_size: float,
        sl_price: float,
        total_trades: int,
    ):
        logger.log_debug("nb_increase_position.py - Calculating")
        entry_size_asset = position_size_asset = min_asset_size
        logger.log_debug("entry_size_asset position_size_asset{entry_size_asset, position_size_asset}")

        entry_size_usd = position_size_usd = round(entry_size_asset * entry_price, 4)
        logger.log_debug("entry_size_usd position_size_usd {entry_size_usd, position_size_usd}")

        average_entry = entry_price
        logger.log_debug("average_entry average_entry}")
        sl_pct = round((average_entry - sl_price) / average_entry, 4)
        logger.log_debug("sl_pct={round(sl_pct*100,2):,}")

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
average_entry= average_entry:,}\n\
entry_price= entry_price:,}\n\
entry_size_asset= entry_size_asset:,}\n\
entry_size_usd= entry_size_usd:,}\n\
position_size_asset= position_size_asset:,}\n\
position_size_usd= position_size_usd:,}\n\
possible_loss= possible_loss:,}\n\
total_trades=total_trades:,}\n\
sl_pct= {round(sl_pct*100,2):,}"
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
