from enum import Enum


class EntrySizeType(Enum):
    AmountEntrySize = 1
    PctAccountEntrySize = 2
    RiskAmountEntrySize = 3
    RiskPctAccountEntrySize = 4


class EntrySize:
    sl_calculator = None
    calculators = {}
    calculate_function = None

    def __init__(
        self,
        sl_calculator,
        entry_size_type: EntrySizeType,
    ):
        self.sl_calculator = sl_calculator
        self.calculators[EntrySizeType.AmountEntrySize] = self.amount_based
        self.calculators[EntrySizeType.PctAccountEntrySize] = self.pctAccount_based
        self.calculators[EntrySizeType.RiskAmountEntrySize] = self.riskAmount_based
        self.calculators[EntrySizeType.RiskPctAccountEntrySize] = self.riskPct_based

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

    def riskPct_based(self):
        print(f"riskPct_based")
