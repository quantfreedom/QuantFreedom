from old_quantfreedom.poly.enums import LeverageType, RejectedOrderError, OrderStatus


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
        return self.calculate_function(**vargs)

    def __calc_liq_price(self, **vargs):
        entry_size = vargs["entry_size"]
        market_fee_pct = vargs["market_fee_pct"]
        leverage = vargs["leverage"]
        average_entry = vargs["average_entry"]
        account_state_cash_used = vargs["account_state_cash_used"]
        account_state_cash_borrowed = vargs["account_state_cash_borrowed"]
        account_state_available_balance = vargs["account_state_available_balance"]
        exchange_settings_mmr_pct = vargs["exchange_settings_mmr_pct"]

        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
        initial_margin = entry_size / leverage
        fee_to_open = entry_size * market_fee_pct  # math checked
        possible_bankruptcy_fee = (
            entry_size * (leverage - 1) / leverage * market_fee_pct
        )
        cash_used_new = (
            initial_margin + fee_to_open + possible_bankruptcy_fee
        )  # math checked

        if cash_used_new > account_state_available_balance * leverage or cash_used_new > account_state_available_balance:
            raise RejectedOrderError(order_status=OrderStatus.CashUsedExceed)

        else:
            # liq formula
            # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
            available_balance_new = account_state_available_balance - cash_used_new
            cash_used_new = account_state_cash_used + cash_used_new
            cash_borrowed_new = account_state_cash_borrowed + entry_size - cash_used_new

            liq_price_new = average_entry * (
                1 - (1 / leverage) + exchange_settings_mmr_pct
            )  # math checked
            return (
                leverage,
                liq_price_new,
                available_balance_new,
                cash_used_new,
                cash_borrowed_new,
            )

    def static(self, **vargs):
        self.__calc_liq_price(self.leverage)

    def dynamic(self, **vargs):
        average_entry = vargs["average_entry"]
        sl_price = vargs["sl_price"]
        market_fee_pct = vargs["market_fee_pct"]

        leverage = round(
            -average_entry
            / (
                sl_price
                - sl_price * 0.001
                - average_entry
                - market_fee_pct * average_entry
                # TODO: revisit the .001 to add to the sl if you make this backtester have the ability to go live
            ),
            1,
        )
        if leverage > self.max_leverage:
            leverage = self.max_leverage
        elif leverage < 1:
            leverage = 1
        vargs["leverage"] = leverage
        return self.__calc_liq_price(
            **vargs,
        )
