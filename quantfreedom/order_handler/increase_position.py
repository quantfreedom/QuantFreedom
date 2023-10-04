from quantfreedom.enums import (
    IncreasePositionType,
    OrderStatus,
    RejectedOrderError,
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
    ):
        self.market_fee_pct = market_fee_pct
        self.risk_account_pct_size = risk_account_pct_size
        self.max_equity_risk_pct = max_equity_risk_pct
        self.max_asset_size = max_asset_size
        self.min_asset_size = min_asset_size

        if stop_loss_type == StopLossStrategyType.SLBasedOnCandleBody:
            if increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                self.calculator_in_pos = self.risk_pct_of_account_and_sl_based_on_in_pos
                self.calculator_not_in_pos = self.risk_pct_of_account_and_sl_based_on_not_in_pos
            elif increase_position_type == IncreasePositionType.AmountEntrySize:
                self.calculator_in_pos = self.amount_based
            elif increase_position_type == IncreasePositionType.PctAccountEntrySize:
                self.calculator_in_pos = self.pctAccount_based
            elif increase_position_type == IncreasePositionType.RiskAmountEntrySize:
                self.calculator_in_pos = self.riskAmount_based
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
        position_size_usd,
        possible_loss,
        sl_price,
    ):
        if in_position:
            (
                average_entry,
                entry_price,
                entry_size_usd,
                position_size_usd,
                possible_loss,
                sl_pct,
            ) = self.calculator_in_pos(
                account_state_equity=account_state_equity,
                average_entry=average_entry,
                entry_price=entry_price,
                position_size_usd=position_size_usd,
                possible_loss=possible_loss,
                sl_price=sl_price,
            )
        else:
            (
                average_entry,
                entry_price,
                entry_size_usd,
                position_size_usd,
                possible_loss,
                sl_pct,
            ) = self.calculator_not_in_pos(
                account_state_equity=account_state_equity,
                entry_price=entry_price,
                possible_loss=possible_loss,
                sl_price=sl_price,
            )

        self.__check_size_value(entry_size_asset=entry_size_usd / entry_price)
        return (
            average_entry,
            entry_price,
            entry_size_usd,
            position_size_usd,
            possible_loss,
            sl_pct,
        )

    def __get_possible_loss(self, account_state_equity, possible_loss):
        possible_loss += account_state_equity * self.risk_account_pct_size  # will this work right?

        if possible_loss > account_state_equity * self.max_equity_risk_pct:
            raise RejectedOrderError("possible loss too big")
        return round(possible_loss, 2)

    def __check_size_value(self, entry_size_asset):
        if self.max_asset_size < entry_size_asset < self.min_asset_size:
            raise RejectedOrderError("Long Increase - Size Value is either to big or too small")

    def amount_based(self, **vargs):
        pass

    def pctAccount_based(self, **vargs):
        pass

    def riskAmount_based(self, **vargs):
        pass

    def smallest_amount(self, **vargs):
        return self.min_asset_size

    def risk_pct_of_account_and_sl_based_on_not_in_pos(
        self,
        account_state_equity,
        entry_price,
        possible_loss,
        sl_price,
    ):
        possible_loss = self.__get_possible_loss(
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
        )
        entry_size_usd = -possible_loss / (
            sl_price / entry_price - 1 - self.market_fee_pct - sl_price * self.market_fee_pct / entry_price
        )
        average_entry = entry_price
        sl_pct = (average_entry - sl_price) / average_entry
        position_size_usd = entry_size_usd

        return (
            average_entry,
            entry_price,
            entry_size_usd,
            position_size_usd,
            possible_loss,
            sl_pct,
        )

    def risk_pct_of_account_and_sl_based_on_in_pos(
        self,
        account_state_equity,
        average_entry,
        entry_price,
        position_size_usd,
        possible_loss,
        sl_price,
    ):
        # need to put in checks to make sure the size isn't too big or goes over or something

        possible_loss = self.__get_possible_loss(
            possible_loss=possible_loss,
            account_state_equity=account_state_equity,
        )

        entry_size_usd = (
            -possible_loss * entry_price * average_entry
            + entry_price * position_size_usd * average_entry
            - sl_price * entry_price * position_size_usd
            + sl_price * entry_price * position_size_usd * self.market_fee_pct
            + entry_price * position_size_usd * average_entry * self.market_fee_pct
        ) / (
            average_entry
            * (entry_price - sl_price + entry_price * self.market_fee_pct + sl_price * self.market_fee_pct)
        )
        if entry_size_usd < 1:
            raise RejectedOrderError(order_status=OrderStatus.EntrySizeTooSmall)
        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        sl_pct = (average_entry - sl_price) / average_entry

        position_size_usd += entry_size_usd

        return (
            average_entry,
            entry_price,
            entry_size_usd,
            position_size_usd,
            possible_loss,
            sl_pct,
        )
