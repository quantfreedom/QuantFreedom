from enum import Enum


class EntrySizeType(Enum):
    AmountEntrySize = 1
    PctAccountEntrySize = 2
    RiskAmountEntrySize = 3
    RiskPctAccountEntrySize = 4


class EntrySize:
    stop_loss_info = None
    init_size_value = None
    calculators = ()
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
        if position_size == 0:
            print("created a position")
        elif position_size > 0:
            print("already in a positon and added to that position")

        print(f"riskPct_based")
