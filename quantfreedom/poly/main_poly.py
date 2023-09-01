
from quantfreedom.poly.polymorphism import StopLossType, TakeProfitType, LongOrder, ShortOrder
from quantfreedom.poly.sizer import SizerType
from enum import Enum

def test_long(sl_type : StopLossType, tp_type : TakeProfitType, sizer_type : SizerType) -> None:
    order = LongOrder(sl_type, tp_type, sizer_type)
    order.stop_loss()
    order.take_profit()
    order.entry_size()
    print('\n')

def test_short(sl_type : StopLossType, tp_type : TakeProfitType, sizer_type : SizerType) -> None:
    order = ShortOrder(sl_type, tp_type, sizer_type)
    order.stop_loss()
    order.take_profit()
    order.entry_size()
    print('\n')

if __name__ == '__main__':
    test_long(StopLossType.SLBasedOnCandleBody, TakeProfitType.RiskReward, SizerType.AmountSizer)
    test_long(StopLossType.SLPct, TakeProfitType.TPPCt, SizerType.PctAccountSizer)
    test_short(StopLossType.SLBasedOnCandleBody, TakeProfitType.RiskReward, SizerType.RiskAmountSizer)
    test_short(StopLossType.SLPct, TakeProfitType.TPPCt, SizerType.RiskPctAccountSizer)