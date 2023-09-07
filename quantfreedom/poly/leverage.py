from quantfreedom.poly.enums import LeverageType


class Leverage:
    calculators = {}
    calculate_function = None
    leverage = None
    max_leverage = None

    def __init__(self, leverage_type: LeverageType, max_leverage: float):
        self.calculators[LeverageType.Static] = self.static
        self.calculators[LeverageType.Dynamic] = self.dynamic
        self.max_leverage = max_leverage

        try:
            self.calculate_function = self.calculators[leverage_type]
        except KeyError as e:
            print(f"Calculator not found -> {repr(e)}")

    def calculate(self, **vargs):
        self.calculate_function()

    def __calc_liq_price(self, leverage_new, size_value):
        if leverage_new > self.max_leverage:
            leverage_new = self.max_leverage
        elif leverage_new < 1:
            leverage_new = 1

        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
        initial_margin = size_value / leverage_new
        fee_to_open = size_value * static_variables_tuple.fee_pct  # math checked
        possible_bankruptcy_fee = (
            size_value * (leverage_new - 1) / leverage_new * static_variables_tuple.fee_pct
        )
        cash_used_new = (
            initial_margin + fee_to_open + possible_bankruptcy_fee
        )  # math checked

        if cash_used_new > available_balance_new * leverage_new:
            raise RejectedOrderError(
                "long inrease iso lev - cash used greater than available balance * lev ... size_value is too big"
            )

        elif cash_used_new > available_balance_new:
            raise RejectedOrderError(
                "long inrease iso lev - cash used greater than available balance ... maybe increase lev"
            )

        else:
            # liq formula
            # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
            available_balance_new = available_balance_new - cash_used_new
            cash_used_new = account_state.cash_used + cash_used_new
            cash_borrowed_new = account_state.cash_borrowed + size_value - cash_used_new

            liq_price_new = average_entry_new * (
                1 - (1 / leverage_new) + static_variables_tuple.mmr_pct
            )  # math checked
            return leverage_new, liq_price_new
        
    def static(self, **vargs):
        self.__calc_liq_price(self.leverage)

    def dynamic(self, **vargs):
        average_entry = vargs["average_entry"]
        sl_price = vargs["sl_price"]
        market_fee_pct = vargs["market_fee_pct"]
        leverage= round(-average_entry / (
            sl_price - sl_price * 0.001 - average_entry - market_fee_pct * average_entry
            #TODO: revisit the .001 to add to the sl if you make this backtester have the ability to go live
        ),1)
        self.__calc_liq_price(leverage_new=leverage, size_value=vargs['size_value'])
