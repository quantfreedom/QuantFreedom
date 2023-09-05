from enum import Enum
from quantfreedom.poly.enums import ExchangeSettings, OrderSettings


class EntrySizeType(Enum):
    AmountEntrySize = 1
    PctAccountEntrySize = 2
    RiskAmountEntrySize = 3
    RiskPctAccountEntrySize = 4


class EntrySize:
    calculator = None
    order_settings = None
    exchange_settings = None

    def __init__(
        self,
        entry_size_type: EntrySizeType,
        exchange_settings: ExchangeSettings,
        order_settings: OrderSettings,
    ):
        if entry_size_type == EntrySizeType.AmountEntrySize:
            self.calculator = self.amount_based
        elif entry_size_type == EntrySizeType.PctAccountEntrySize:
            self.calculator = self.pctAccount_based
        elif entry_size_type == EntrySizeType.RiskAmountEntrySize:
            self.calculator = self.riskAmount_based
        elif entry_size_type == EntrySizeType.RiskPctAccountEntrySize:
            self.calculator = self.risk_pct_of_account

        self.order_settings = order_settings
        self.exchange_settings = exchange_settings

    def calculate(self, **vargs):
        self.calculator(**vargs)

    def amount_based(self, **vargs):
        print("amount_based")

    def pctAccount_based(self, **vargs):
        print("pctAccount_based")

    def riskAmount_based(self, **vargs):
        print(f"riskAmount_based")

    def risk_pct_of_account(self, **vargs):
        print("risk_pct_of_account\n")
        possible_loss = (
            vargs["account_state_equity"] * self.order_settings.risk_account_pct_size
        )
        sl_price = vargs["sl_price"]
        entry_price = vargs["entry_price"]
        market_fee_pct = self.exchange_settings.market_fee_pct

        size_value = -possible_loss / (
            sl_price / entry_price
            - 1
            - market_fee_pct
            - sl_price * market_fee_pct / entry_price
        )
        print("Here is the possible loss: ", possible_loss)
        print("the size to use is: ", size_value)
        print("the ")
