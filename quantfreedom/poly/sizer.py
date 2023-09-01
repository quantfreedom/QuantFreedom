from enum import Enum

class SizerType(Enum):
    AmountSizer = 1
    PctAccountSizer = 2
    RiskAmountSizer = 3
    RiskPctAccountSizer = 4

class Sizer:
    sl_calculator = None
    calculators = {}
    calculate_function = None

    def __init__(self, sl_calculator, sizer_type : SizerType):
        self.sl_calculator = sl_calculator
        self.calculators[SizerType.AmountSizer] = self.amount_based
        self.calculators[SizerType.PctAccountSizer] = self.pctAccount_based
        self.calculators[SizerType.RiskAmountSizer] = self.riskAmount_based
        self.calculators[SizerType.RiskPctAccountSizer] = self.riskPct_based

        try:
            self.calculate_function = self.calculators[sizer_type]
        except KeyError as e:
            print(f'Calculator not found -> {repr(e)}')

    def calculate(self):
        self.calculate_function()

    def amount_based(self):
        print('amount_based')

    def pctAccount_based(self):
        print('pctAccount_based')

    def riskAmount_based(self):
        print(f'riskAmount_based -> {self.sl_calculator.get_result()}')

    def riskPct_based(self):
        print(f'riskPct_based -> {self.sl_calculator.get_result()}')


    