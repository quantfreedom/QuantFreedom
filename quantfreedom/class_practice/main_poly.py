import numpy as np
import pandas as pd



account_state = AccountState()
order_settings = OrderSettings()
exchange_settings = ExchangeSettings()

# candles_dt = np.dtype(
#     [
#         ("open", np.float_),
#         ("high", np.float_),
#         ("low", np.float_),
#         ("close", np.float_),
#     ],
#     align=True,
# )

price_data = pd.read_hdf("../../tests/data/prices.hd5")


def test_long(
    sl_type: StopLossType,
    candle_body: CandleBody,
    tp_type: TakeProfitType,
    entry_size_type: EntrySizeType,
    leverage_type: LeverageType,
    account_state: AccountState,
    order_settings: OrderSettings,
    price_data: pd.DataFrame,
    exchange_settings: ExchangeSettings,
) -> None:
    order = LongOrder(
        sl_type=sl_type,
        candle_body=candle_body,
        tp_type=tp_type,
        entry_size_type=entry_size_type,
        leverage_type=leverage_type,
        account_state=account_state,
        order_settings=order_settings,
        price_data=price_data,
        exchange_settings=exchange_settings,
    )
    sl_price = order.calc_stop_loss()
    order.calc_entry_size(
        sl_price=sl_price,
        entry_price=price_data.close[-1],
        market_fee_pct=exchange_settings.market_fee_pct,
    )
    order.calc_leverage()
    order.calc_take_profit()
    print("\n")


if __name__ == "__main__":
    test_long(
        entry_size_type=EntrySizeType.RiskPctAccountEntrySize,
        sl_type=StopLossType.SLBasedOnCandleBody,
        candle_body=CandleBody.Low,
        leverage_type=LeverageType.Dynamic,
        tp_type=TakeProfitType.RiskReward,
        account_state=account_state,
        order_settings=order_settings,
        price_data=price_data.BTCUSDT[-30:],
        exchange_settings=exchange_settings,
    )
