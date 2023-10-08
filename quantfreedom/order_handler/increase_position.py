from quantfreedom.custom_logger import CustomLogger
from quantfreedom.enums import (
    IncreasePositionType,
    OrderStatus,
    RejectedOrder,
    StopLossStrategyType,
)
import logging

from quantfreedom.helper_funcs import round_size_by_tick_step

info_logger = logging.getLogger("info")


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
        price_tick_step: float,
        asset_tick_step: float,
    ):
        self.market_fee_pct = market_fee_pct
        self.risk_account_pct_size = risk_account_pct_size
        self.max_equity_risk_pct = max_equity_risk_pct
        self.max_asset_size = max_asset_size
        self.min_asset_size = min_asset_size
        self.entry_size_asset = entry_size_asset
        self.max_trades = int(max_trades)
        self.price_tick_step = price_tick_step
        self.asset_tick_step = asset_tick_step

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
        if in_position:
            info_logger.debug("We are in a position")
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
            info_logger.debug("Not in a position")
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

        self.__check_size_too_big_or_small(entry_size_asset=entry_size_asset)
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

    def __check_size_too_big_or_small(self, entry_size_asset):
        if entry_size_asset < self.min_asset_size:
            raise RejectedOrder(
                msg=f"Entry Size too small {entry_size_asset} min_asset_size={self.min_asset_size}",
                order_status=OrderStatus.EntrySizeTooSmall,
            )

        elif entry_size_asset > self.max_asset_size:
            raise RejectedOrder(
                msg=f"Entry Size too big {entry_size_asset} max asset size={self.max_asset_size}",
                order_status=OrderStatus.EntrySizeTooBig,
            )
        info_logger.debug(f"Entry size is fine")

    def __pl_risk_account_pct_size(self, account_state_equity, possible_loss, total_trades):
        possible_loss = round(possible_loss + account_state_equity * self.risk_account_pct_size)
        max_equity_risk = round(account_state_equity * self.max_equity_risk_pct)
        if possible_loss > max_equity_risk:
            raise RejectedOrder(
                msg=f"PL too big {possible_loss} max risk={max_equity_risk}",
                order_status=OrderStatus.PossibleLossTooBig,
            )
        total_trades += 1
        info_logger.debug(f"Possible Loss is fine")
        return possible_loss, total_trades

    def __tt_amount_based(
        self,
        average_entry,
        possible_loss,
        position_size_asset,
        sl_price,
        total_trades,
    ):
        pnl = position_size_asset * (sl_price - average_entry)  # math checked
        fee_open = position_size_asset * average_entry * self.market_fee_pct  # math checked
        fee_close = position_size_asset * sl_price * self.market_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        possible_loss = round(-(pnl - fees_paid), 4)

        total_trades += 1
        if total_trades > self.max_trades:
            raise RejectedOrder(
                msg=f"Max Trades to big {total_trades} mt={self.max_trades}",
                order_status=OrderStatus.HitMaxTrades,
            )
        info_logger.debug(f"total trades is fine")
        return possible_loss, total_trades

    def smallest_entry_size_asset_not_in_pos(
        self,
        account_state_equity,
        entry_price,
        possible_loss,
        sl_price,
        total_trades,
    ):
        info_logger.debug("Calculating")
        entry_size_asset = position_size_asset = self.min_asset_size
        entry_size_usd = position_size_usd = round(entry_size_asset * entry_price, 4)
        average_entry = entry_price
        sl_pct = round((average_entry - sl_price) / average_entry, 4)

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
        info_logger.debug("Calculating")

        position_size_asset += self.min_asset_size
        entry_size_asset = self.min_asset_size

        entry_size_usd = round(self.min_asset_size * entry_price, 4)

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=self.price_tick_step,
        )
        sl_pct = round((average_entry - sl_price) / average_entry, 4)

        position_size_usd = round(entry_size_usd + position_size_usd, 4)
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
        info_logger.debug("Calculating")
        possible_loss, total_trades = self.get_possible_loss_or_trades(
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
            total_trades=total_trades,
        )
        entry_size_usd = position_size_usd = round(
            -possible_loss
            / (sl_price / entry_price - 1 - self.market_fee_pct - sl_price * self.market_fee_pct / entry_price),
            4,
        )
        average_entry = entry_price
        sl_pct = round((average_entry - sl_price) / average_entry, 4)
        entry_size_asset = position_size_asset = round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=self.asset_tick_step,
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
        info_logger.debug("Calculating")
        possible_loss, total_trades = self.get_possible_loss_or_trades(
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
            total_trades=total_trades,
        )

        entry_size_usd = round(
            -(
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
            ),
            4,
        )
        position_size_usd = round(entry_size_usd + position_size_usd, 4)

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )

        average_entry = round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=self.price_tick_step,
        )

        sl_pct = round((average_entry - sl_price) / average_entry, 4)

        entry_size_asset = round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=self.asset_tick_step,
        )
        position_size_asset = round_size_by_tick_step(
            user_num=position_size_asset + entry_size_asset,
            exchange_num=self.asset_tick_step,
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
