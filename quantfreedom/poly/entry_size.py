from quantfreedom.enums.enums import RejectedOrderError
from quantfreedom.poly.enums import (
    ExchangeSettings,
    OrderSettings,
    EntrySizeType,
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
        if vargs["in_pos"]:
            size_value = self.calculator_in_pos(**vargs)
        else:
            size_value = self.calculator_not_in_pos(**vargs)

        self.__check_size_value(size_value=size_value)
        return size_value

    def __get_possible_loss(self, **vargs):
        account_state_equity = vargs["account_state_equity"]
        
        possible_loss = (
            account_state_equity * self.order_settings.risk_account_pct_size
        ) + vargs["order_result"].possible_loss
        
        if possible_loss > account_state_equity * self.order_settings.max_equity_risk_pct:
            raise RejectedOrderError(
                "possible loss too big"
            )
        return (
            possible_loss,
            vargs["sl_price"],
            vargs["entry_price"],
            self.exchange_settings.market_fee_pct,
        )

    def __check_size_value(self, size_value):
        if (
            size_value < 1
            or size_value > self.exchange_settings.max_order_size_value
            or size_value < self.exchange_settings.min_order_size_value
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
        print("risk_pct_of_account and sl_based and not_in_pos\n")
        possible_loss, sl_price, entry_price, market_fee_pct = self.__get_possible_loss(
            **vargs
        )

        size_value = -possible_loss / (
            sl_price / entry_price
            - 1
            - market_fee_pct
            - sl_price * market_fee_pct / entry_price
        )
        
        return size_value, entry_price

    def risk_pct_of_account_and_sl_based_on_in_pos(self, **vargs):
        possible_loss, sl_price, entry_price, market_fee_pct = self.__get_possible_loss(
            **vargs
        )
        average_entry = vargs["order_result"].average_entry
        current_pos_size = vargs["order_result"].position_size
        size_value = (
            -possible_loss * entry_price * average_entry
            + entry_price * current_pos_size * average_entry
            - sl_price * entry_price * current_pos_size
            + sl_price * entry_price * current_pos_size * market_fee_pct
            + entry_price * current_pos_size * average_entry * market_fee_pct
        ) / (
            average_entry
            * (
                entry_price
                - sl_price
                + entry_price * market_fee_pct
                + sl_price * market_fee_pct
            )
        )
        average_entry_new = (size_value + current_pos_size) / (
            (size_value / entry_price) + (current_pos_size / average_entry_new)
        )
        return size_value, average_entry_new
