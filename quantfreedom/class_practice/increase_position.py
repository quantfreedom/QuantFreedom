from quantfreedom.class_practice.enums import (
    IncreasePositionType,
    StopLossType,
)


class IncreasePositionLong:
    calculator_in_pos = None
    calculator_not_in_pos = None

    def __init__(
        self,
        increase_position_type: int,
        stop_loss_type: int,
    ):
        if stop_loss_type == StopLossType.SLBasedOnCandleBody:
            if increase_position_type == IncreasePositionType.AmountEntrySize:
                self.calculator_in_pos = self.amount_based
            elif increase_position_type == IncreasePositionType.PctAccountEntrySize:
                self.calculator_in_pos = self.pctAccount_based
            elif increase_position_type == IncreasePositionType.RiskAmountEntrySize:
                self.calculator_in_pos = self.riskAmount_based
            elif increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                self.calculator_in_pos = self.risk_pct_of_account_and_sl_based_on_in_pos
                self.calculator_not_in_pos = (
                    self.risk_pct_of_account_and_sl_based_on_not_in_pos
                )
            else:
                raise NotImplementedError(
                    "IncreasePositionType=RiskPctAccountEntrySize and not StopLossType=SLBasedOnCandleBody"
                )

    def calculate_increase_posotion(self, **vargs):
        if vargs["in_position"]:
            self.calculator_in_pos(**vargs)
        else:
            self.calculator_not_in_pos(**vargs)

        self.__check_size_value()

    def __get_possible_loss(self, **vargs):
        print("Long Order - Increase Position - __get_possible_loss")

    def __check_size_value(self):
        print("Long Order - Increase Position - __check_size_value")

    def amount_based(self, **vargs):
        print("amount_based")

    def pctAccount_based(self, **vargs):
        print("pctAccount_based")

    def riskAmount_based(self, **vargs):
        print(f"riskAmount_based")

    def risk_pct_of_account_and_sl_based_on_not_in_pos(self, **vargs):
        self.__get_possible_loss(**vargs)
        print(
            "Long Order - Increase Position - risk_pct_of_account_and_sl_based_on_not_in_pos"
        )

    def risk_pct_of_account_and_sl_based_on_in_pos(self, **vargs):
        self.__get_possible_loss(**vargs)
        print("Long Order - Increase Position - risk_pct_of_account_and_sl_based_on_in_pos")
