from quantfreedom.poly.long_short_orders import LongOrder, ShortOrder
from quantfreedom.poly.stop_loss import StopLossType
from quantfreedom.poly.leverage import LeverageType
from quantfreedom.poly.entry_size import EntrySizeType
from quantfreedom.poly.take_profit import TakeProfitType


def test_long(
    sl_type: StopLossType,
    tp_type: TakeProfitType,
    entry_size_type: EntrySizeType,
    leverage_type: LeverageType,
) -> None:
    order = LongOrder(sl_type, tp_type, entry_size_type, leverage_type)
    order.calc_stop_loss()
    order.calc_leverage()
    order.calc_entry_size()
    order.calc_take_profit()
    print("\n")


def test_short(
    sl_type: StopLossType,
    tp_type: TakeProfitType,
    entry_size_type: EntrySizeType,
    leverage_type: LeverageType,
) -> None:
    order = ShortOrder(sl_type, tp_type, entry_size_type, leverage_type)
    order.calc_stop_loss()
    order.calc_leverage()
    order.calc_entry_size()
    order.calc_take_profit()
    print("\n")


if __name__ == "__main__":
    test_long(
        StopLossType.SLBasedOnCandleBody,
        LeverageType.Dynamic,
        EntrySizeType.AmountEntrySize,
        TakeProfitType.RiskReward,
    )
    test_long(
        StopLossType.SLPct,
        LeverageType.Static,
        EntrySizeType.PctAccountEntrySize,
        TakeProfitType.TPPct,
    )
    test_short(
        StopLossType.SLBasedOnCandleBody,
        LeverageType.Dynamic,
        EntrySizeType.RiskAmountEntrySize,
        TakeProfitType.RiskReward,
    )
    test_short(
        StopLossType.SLPct,
        LeverageType.Static,
        EntrySizeType.RiskPctAccountEntrySize,
        TakeProfitType.TPPct,
    )
