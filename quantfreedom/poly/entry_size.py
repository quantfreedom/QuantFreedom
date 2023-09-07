from quantfreedom.poly.enums import ExchangeSettings, OrderSettings, EntrySizeType, StopLossType


class EntrySize:
    calculator_in_pos = None
    order_settings = None
    exchange_settings = None

    def __init__(
        self,
        entry_size_type: EntrySizeType,
        exchange_settings: ExchangeSettings,
        order_settings: OrderSettings
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
                self.calculator_not_in_pos = self.risk_pct_of_account_and_sl_based_on_not_in_pos
            else:
                raise NotImplementedError('EntrySizeType=RiskPctAccountEntrySize and not StopLossType=SLBasedOnCandleBody')

        self.order_settings = order_settings
        self.exchange_settings = exchange_settings

    def calculate(self, **vargs):
        if vargs['in_pos']:
            self.calculator_in_pos(**vargs)
        else:
            self.calculator_not_in_pos(**vargs)

    def __get_possible_loss(self, **vargs):
        possible_loss = (
            vargs["account_state_equity"] * self.order_settings.risk_account_pct_size
        )
        sl_price = vargs["sl_price"]
        entry_price = vargs["entry_price"]
        market_fee_pct = self.exchange_settings.market_fee_pct
    
    def amount_based(self, **vargs):
        print("amount_based")

    def pctAccount_based(self, **vargs):
        print("pctAccount_based")

    def riskAmount_based(self, **vargs):
        print(f"riskAmount_based")

    def risk_pct_of_account_and_sl_based_on_not_in_pos(self, **vargs):
        print("risk_pct_of_account and sl_based and not_in_pos\n")
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

    def risk_pct_of_account_and_sl_based_on_in_pos(self, **vargs):
        print("risk_pct_of_account and sl_based and in_pos\n")

        possible_loss = (
            vargs["account_state_equity"] * self.order_settings.risk_account_pct_size
        )
        sl_price = vargs["sl_price"]
        entry_price = vargs["entry_price"]
        market_fee_pct = self.exchange_settings.market_fee_pct