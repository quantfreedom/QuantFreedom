from quantfreedom.poly.polymorphism import (
    StopLossType,
    TakeProfitType,
    LongOrder,
    ShortOrder,
)
from quantfreedom.poly.sizer import SizerType
from quantfreedom.poly.leverage import LeverageType


def test_long(
    sl_type: StopLossType,
    tp_type: TakeProfitType,
    sizer_type: SizerType,
    leverage_type: LeverageType,
) -> None:
    order = LongOrder(sl_type, tp_type, sizer_type, leverage_type)
    order.stop_loss()
    order.calc_leverage()
    order.entry_size()
    order.take_profit()
    print("\n")


def test_short(
    sl_type: StopLossType,
    tp_type: TakeProfitType,
    sizer_type: SizerType,
    leverage_type: LeverageType,
) -> None:
    order = ShortOrder(sl_type, tp_type, sizer_type, leverage_type)
    order.stop_loss()
    order.calc_leverage()
    order.entry_size()
    order.take_profit()
    print("\n")


if __name__ == "__main__":
    test_long(
        StopLossType.SLBasedOnCandleBody,
        TakeProfitType.RiskReward,
        SizerType.AmountSizer,
        LeverageType.Dynamic,
    )
    test_long(
        StopLossType.SLPct,
        TakeProfitType.TPPCt,
        SizerType.PctAccountSizer,
        LeverageType.Static,
    )
    test_short(
        StopLossType.SLBasedOnCandleBody,
        TakeProfitType.RiskReward,
        SizerType.RiskAmountSizer,
        LeverageType.Dynamic,
    )
    test_short(
        StopLossType.SLPct,
        TakeProfitType.TPPCt,
        SizerType.RiskPctAccountSizer,
        LeverageType.Static,
    )
