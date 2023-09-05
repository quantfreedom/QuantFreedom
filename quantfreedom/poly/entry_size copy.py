from enum import Enum


class EntrySizeType(Enum):
    AmountEntrySize = 1
    PctAccountEntrySize = 2
    RiskAmountEntrySize = 3
    RiskPctAccountEntrySize = 4


class EntrySize:
    stop_loss_info = None
    init_size_value = None
    calculators = {}
    calculate_function = None

    def __init__(
        self,
        stop_loss_info,
        entry_size_type: EntrySizeType,
    ):
        self.stop_loss_info = stop_loss_info
        self.calculators[EntrySizeType.AmountEntrySize] = self.amount_based
        self.calculators[EntrySizeType.PctAccountEntrySize] = self.pctAccount_based
        self.calculators[EntrySizeType.RiskAmountEntrySize] = self.riskAmount_based
        self.calculators[
            EntrySizeType.RiskPctAccountEntrySize
        ] = self.risk_pct_of_account

        try:
            self.calculate_function = self.calculators[entry_size_type]
        except KeyError as e:
            print(f"Calculator not found -> {repr(e)}")

    def calculate(self):
        self.calculate_function()

    def amount_based(self):
        print("amount_based")

    def pctAccount_based(self):
        print("pctAccount_based")

    def riskAmount_based(self):
        print(f"riskAmount_based")

    def risk_pct_of_account(self):
        trade_possible_loss = -(equity * risk_pct_of_account_value)
        if position_size == 0:
            size_value = trade_possible_loss / (
                sl_price / entry - 1 - fee_pct - sl_price * fee_pct / entry
            )
            position_possible_loss = trade_possible_loss
        elif position_size > 0:
            position_possible_loss = trade_possible_loss + position_possible_loss
            size_value = (
                position_possible_loss
                * trade_entry
                * average_entry
                + trade_entry * position_size * average_entry
                - sl_price_new * trade_entry * position_size
                + sl_price_new * trade_entry * position_size * fee_pct
                + trade_entry * position_size * average_entry * fee_pct
            ) / (
                average_entry
                * (
                    trade_entry
                    - sl_price_new
                    + trade_entry * fee_pct
                    + sl_price_new * fee_pct
                )
            )

        print(f"riskPct_based")
