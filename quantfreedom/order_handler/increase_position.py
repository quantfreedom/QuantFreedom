from quantfreedom.custom_logger import CustomLogger
from quantfreedom.enums import (
    IncreasePositionType,
    OrderStatus,
    RejectedOrder,
    StopLossStrategyType,
)


class IncreasePositionLong:
    calculator_in_pos = None
    calculator_not_in_pos = None

    market_fee_pct = None
    risk_account_pct_size = None
    max_equity_risk_pct = None
    max_asset_size = None
    min_asset_size = None

    def __init__(
        self,
        increase_position_type: int,
        stop_loss_type: int,
        market_fee_pct: float,
        risk_account_pct_size: float,
        max_equity_risk_pct: float,
        max_asset_size: float,
        min_asset_size: float,
        entry_size_asset: float,
        max_trades: int,
        logger: CustomLogger,
    ):
        self.market_fee_pct = market_fee_pct
        self.risk_account_pct_size = risk_account_pct_size
        self.max_equity_risk_pct = max_equity_risk_pct
        self.max_asset_size = max_asset_size
        self.min_asset_size = min_asset_size
        self.info_logger = logger.info_logger
        self.entry_size_asset = entry_size_asset
        self.max_trades = max_trades

        if stop_loss_type == StopLossStrategyType.SLBasedOnCandleBody:
            if increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                self.calculator_not_in_pos = self.risk_pct_of_account_and_sl_based_on_not_in_pos
                self.calculator_in_pos = self.risk_pct_of_account_and_sl_based_on_in_pos
                self.get_possible_loss_or_trades = self.__pl_risk_account_pct_size

            elif increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
                self.calculator_not_in_pos = self.smallest_entry_size_asset_not_in_pos
                self.calculator_in_pos = self.smallest_entry_size_asset_in_pos
                self.get_possible_loss_or_trades = self.__tt_amount_based

            else:
                raise NotImplementedError(
                    "IncreasePositionType=RiskPctAccountEntrySize and not StopLossStrategyType=SLBasedOnCandleBody"
                )

    def calculate_increase_posotion(
        self,
        account_state_equity,
        average_entry,
        entry_price,
        in_position,
        position_size_asset,
        position_size_usd,
        possible_loss,
        sl_price,
        total_trades,
    ):
        self.info_logger.debug("")
        if in_position:
            (
                average_entry,
                entry_price,
                entry_size_asset,
                entry_size_usd,
                position_size_asset,
                position_size_usd,
                possible_loss,
                total_trades,
                sl_pct,
            ) = self.calculator_in_pos(
                account_state_equity=account_state_equity,
                average_entry=average_entry,
                entry_price=entry_price,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
                possible_loss=possible_loss,
                sl_price=sl_price,
                total_trades=total_trades,
            )
        else:
            (
                average_entry,
                entry_price,
                entry_size_asset,
                entry_size_usd,
                position_size_asset,
                position_size_usd,
                possible_loss,
                total_trades,
                sl_pct,
            ) = self.calculator_not_in_pos(
                account_state_equity=account_state_equity,
                entry_price=entry_price,
                possible_loss=possible_loss,
                sl_price=sl_price,
                total_trades=total_trades,
            )

        self.__check_size_value(entry_size_asset=entry_size_asset)
        self.info_logger.info(
            f"\n\n\
average_entry={average_entry}  entry_price={entry_price} entry_size_asset={entry_size_asset}\n\
entry_size_usd={entry_size_usd} position_size_asset={position_size_asset}, position_size_usd={position_size_usd}\n\
possible_loss={possible_loss} total_trades={total_trades}, sl_pct={sl_pct}\n"
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

    def __pl_risk_account_pct_size(self, account_state_equity, possible_loss, total_trades):
        self.info_logger.debug("")
        possible_loss = round(possible_loss + account_state_equity * self.risk_account_pct_size)
        max_equity_risk = round(account_state_equity * self.max_equity_risk_pct)
        if possible_loss > max_equity_risk:
            raise RejectedOrder(
                msg=f"Possible loss = {possible_loss} max risk = {max_equity_risk}",
                order_status=OrderStatus.PossibleLossTooBig,
            )
        total_trades += 1
        return possible_loss, total_trades

    def __tt_amount_based(
        self,
        average_entry,
        possible_loss,
        position_size_asset,
        sl_price,
        total_trades,
    ):
        self.info_logger.debug("")
        pnl = position_size_asset * (sl_price - average_entry)  # math checked
        fee_open = position_size_asset * average_entry * self.market_fee_pct  # math checked
        fee_close = position_size_asset * sl_price * self.market_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        possible_loss = -(pnl - fees_paid)

        total_trades += 1
        if total_trades > self.max_trades:
            raise RejectedOrder(
                msg=f"Too many trades - Total trades={total_trades} max trades={self.max_trades}",
                order_status=OrderStatus.HitMaxTrades,
            )
        return possible_loss, total_trades

    def __check_size_value(self, entry_size_asset):
        self.info_logger.debug("")
        if entry_size_asset < self.min_asset_size:
            raise RejectedOrder(
                msg=f"Size of asset too small entry_size_asset={entry_size_asset} min_asset_size{self.min_asset_size}",
                order_status=OrderStatus.EntrySizeTooSmall,
            )

        elif entry_size_asset > self.max_asset_size:
            raise RejectedOrder(
                msg=f"Asset Size too big - entry size asset={entry_size_asset} max asset size={self.max_asset_size}",
                order_status=OrderStatus.EntrySizeTooBig,
            )

    def smallest_entry_size_asset_not_in_pos(
        self,
        account_state_equity,
        entry_price,
        possible_loss,
        sl_price,
        total_trades,
    ):
        self.info_logger.debug("")
        entry_size_asset = position_size_asset = self.min_asset_size
        entry_size_usd = position_size_usd = round(entry_size_asset * entry_price, 4)
        average_entry = entry_price
        sl_pct = (average_entry - sl_price) / average_entry

        possible_loss, total_trades = self.get_possible_loss_or_trades(
            possible_loss=possible_loss,
            total_trades=total_trades,
            position_size_asset=position_size_asset,
            sl_price=sl_price,
            average_entry=average_entry,
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

    def smallest_entry_size_asset_in_pos(
        self,
        account_state_equity,
        average_entry,
        entry_price,
        possible_loss,
        position_size_asset,
        position_size_usd,
        sl_price,
        total_trades,
    ):
        # need to put in checks to make sure the size isn't too big or goes over or something
        self.info_logger.debug("")

        position_size_asset += self.min_asset_size
        entry_size_asset = self.min_asset_size

        entry_size_usd = round(self.min_asset_size * entry_price, 4)

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        sl_pct = (average_entry - sl_price) / average_entry

        position_size_usd += entry_size_usd
        possible_loss, total_trades = self.get_possible_loss_or_trades(
            total_trades=total_trades,
            average_entry=average_entry,
            possible_loss=possible_loss,
            sl_price=sl_price,
            position_size_asset=position_size_asset,
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

    def risk_pct_of_account_and_sl_based_on_not_in_pos(
        self,
        account_state_equity,
        entry_price,
        possible_loss,
        sl_price,
        total_trades,
    ):
        self.info_logger.debug("")
        possible_loss, total_trades = self.get_possible_loss_or_trades(
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
            total_trades=total_trades,
        )
        entry_size_usd = position_size_usd = -possible_loss / (
            sl_price / entry_price - 1 - self.market_fee_pct - sl_price * self.market_fee_pct / entry_price
        )
        average_entry = entry_price
        sl_pct = (average_entry - sl_price) / average_entry
        entry_size_asset = position_size_asset = entry_size_usd / entry_price

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

    def risk_pct_of_account_and_sl_based_on_in_pos(
        self,
        account_state_equity,
        average_entry,
        entry_price,
        possible_loss,
        position_size_asset,
        position_size_usd,
        sl_price,
        total_trades,
    ):
        # need to put in checks to make sure the size isn't too big or goes over or something
        self.info_logger.debug("")
        possible_loss, total_trades = self.get_possible_loss_or_trades(
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
            total_trades=total_trades,
        )

        entry_size_usd = -(
            (
                -possible_loss * entry_price * average_entry
                + entry_price * position_size_usd * average_entry
                - sl_price * entry_price * position_size_usd
                + sl_price * entry_price * position_size_usd * self.market_fee_pct
                + entry_price * position_size_usd * average_entry * self.market_fee_pct
            )
            / (
                average_entry
                * (entry_price - sl_price + entry_price * self.market_fee_pct + sl_price * self.market_fee_pct)
            )
        )
        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        sl_pct = (average_entry - sl_price) / average_entry

        position_size_usd += entry_size_usd
        entry_size_asset = entry_size_usd / entry_price
        position_size_asset += entry_size_asset
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
