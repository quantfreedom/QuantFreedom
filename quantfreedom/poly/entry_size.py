from quantfreedom.enums.enums import RejectedOrderError
from quantfreedom.poly.enums import (
    ExchangeSettings,
    OrderSettings,
    EntrySizeType,
    OrderStatus,
    StopLossType,
)


class EntrySize:
    calculator_in_pos = None
    order_settings = None
    exchange_settings = None

    def __init__(
        self,
        entry_size_type: EntrySizeType,
        exchange_settings: ExchangeSettings,
        order_settings: OrderSettings,
    ):
        if entry_size_type == EntrySizeType.AmountEntrySize:
            self.calculator_in_pos = self.amount_based
        elif entry_size_type == EntrySizeType.PctAccountEntrySize:
            self.calculator_in_pos = self.pctAccount_based
        elif entry_size_type == EntrySizeType.RiskAmountEntrySize:
            self.calculator_in_pos = self.riskAmount_based
        elif entry_size_type == EntrySizeType.RiskPctAccountEntrySize:
            if order_settings.stop_loss_type == StopLossType.SLBasedOnCandleBody:
                self.calculator_in_pos = self.risk_pct_of_account_and_sl_based_on_in_pos
                self.calculator_not_in_pos = (
                    self.risk_pct_of_account_and_sl_based_on_not_in_pos
                )
            else:
                raise NotImplementedError(
                    "EntrySizeType=RiskPctAccountEntrySize and not StopLossType=SLBasedOnCandleBody"
                )

        self.order_settings = order_settings
        self.exchange_settings = exchange_settings

    def calculate(self, **vargs):
        if vargs["in_position"]:
            (
                entry_size,
                position_size,
                entry_price,
                average_entry,
                possible_loss,
                sl_pct,
            ) = self.calculator_in_pos(**vargs)
        else:
            (
                entry_size,
                position_size,
                entry_price,
                average_entry,
                possible_loss,
                sl_pct,
            ) = self.calculator_not_in_pos(**vargs)

        self.__check_size_value(entry_size=entry_size)
        return (
            entry_size,
            position_size,
            entry_price,
            average_entry,
            possible_loss,
            sl_pct,
        )

    def decrease_position_size(self, **vargs):
        """
        This is where the long position gets decreased or closed out.
        """
        position_size = vargs['position_size']
        entry_price = vargs['entry_price']
        average_entry = vargs['average_entry']
        market_fee_pct = vargs['market_fee_pct']
        limit_fee_pct = vargs['limit_fee_pct']

        # profit and loss calulation
        coin_size = position_size / average_entry  # math checked
        pnl = coin_size * (
            entry_price - average_entry
        )  # math checked
        fee_open = coin_size * average_entry * market_fee_pct  # math checked
        fee_close = coin_size * entry_price * limit_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        realized_pnl = pnl - fees_paid  # math checked
        
        position_size = 0.
        
        return fees_paid, OrderStatus.Filled, position_size, realized_pnl
        

    def __get_possible_loss(self, **vargs):
        account_state_equity = vargs["account_state_equity"]

        possible_loss = (
            account_state_equity * self.order_settings.risk_account_pct_size
        ) + vargs["possible_loss"]

        if (
            possible_loss
            > account_state_equity * self.order_settings.max_equity_risk_pct
        ):
            raise RejectedOrderError("possible loss too big")
        return (
            possible_loss,
            vargs["sl_price"],
            vargs["entry_price"],
        )

    def __check_size_value(self, entry_size):
        if (
            entry_size < 1
            or entry_size > self.exchange_settings.max_order_size_value
            or entry_size < self.exchange_settings.min_order_size_value
        ):
            raise RejectedOrderError(
                "Long Increase - Size Value is either to big or too small"
            )

    def amount_based(self, **vargs):
        print("amount_based")

    def pctAccount_based(self, **vargs):
        print("pctAccount_based")

    def riskAmount_based(self, **vargs):
        print(f"riskAmount_based")

    def risk_pct_of_account_and_sl_based_on_not_in_pos(self, **vargs):
        possible_loss, sl_price, entry_price = self.__get_possible_loss(**vargs)
        market_fee_pct = self.exchange_settings.market_fee_pct
        entry_size = -possible_loss / (
            sl_price / entry_price
            - 1
            - market_fee_pct
            - sl_price * market_fee_pct / entry_price
        )
        entry_size = round(entry_size, 2)
        average_entry = entry_price
        sl_pct = 100 - sl_price * 100 / average_entry
        sl_pct = round(sl_pct, 2)
        position_size = entry_size
        return (
            entry_size,
            position_size,
            entry_price,
            average_entry,
            possible_loss,
            sl_pct,
        )

    def risk_pct_of_account_and_sl_based_on_in_pos(self, **vargs):
        possible_loss, sl_price, entry_price = self.__get_possible_loss(**vargs)
        market_fee_pct = self.exchange_settings.market_fee_pct
        average_entry = vargs["average_entry"]
        position_size = vargs["position_size"]

        entry_size = (
            -possible_loss * entry_price * average_entry
            + entry_price * position_size * average_entry
            - sl_price * entry_price * position_size
            + sl_price * entry_price * position_size * market_fee_pct
            + entry_price * position_size * average_entry * market_fee_pct
        ) / (
            average_entry
            * (
                entry_price
                - sl_price
                + entry_price * market_fee_pct
                + sl_price * market_fee_pct
            )
        )
        average_entry_new = (entry_size + position_size) / (
            (entry_size / entry_price) + (position_size / average_entry)
        )
        sl_pct = 100 - sl_price * 100 / average_entry
        position_size += entry_size
        return (
            entry_size,
            position_size,
            entry_price,
            average_entry_new,
            possible_loss,
            sl_pct,
        )
