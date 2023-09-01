

from enum import Enum

class StopLossType(Enum):
    SLBasedOnCandleBody = 1
    SLPct = 2
    
class TakeProfitType(Enum):
    RiskReward = 1
    TPPCt = 2

class Order:
    sl_calculator = None
    tp_calculator = None

    def __init__(self, sl_type : StopLossType, tp_type : TakeProfitType):
        self.sl_calculator = StopLossCalculator.create(sl_type)
        self.tp_calculator = TakeProfitCalculator.create(tp_type)

    def stop_loss():
        raise NotImplemented()
    
    def take_profit():
        raise NotImplemented()

    def entry_size():
        raise NotImplemented()

class StopLossCalculator:
    def create(type : StopLossType):
         return SLBasedOnCandleBody() if type == StopLossType.SLBasedOnCandleBody else SLPct()
   
    def calculate(self):
        raise NotImplemented()
    
class TakeProfitCalculator:
    def create(type : TakeProfitType):
         return RiskReward() if type == TakeProfitType.RiskReward else TPPCt()
   
    def calculate(self):
        raise NotImplemented()
    

class RiskReward(TakeProfitCalculator):
    def calculate(self):
        print('RiskReward')

class TPPCt(TakeProfitCalculator):
    def calculate(self):
        print('TPPCt')

class SLBasedOnCandleBody(StopLossCalculator):
    def calculate(self):
        print('SLBasedOnCandleBody')

class SLPct(StopLossCalculator):
    def calculate(self):
        print('SLPct')

class LongOrder(Order):
    def stop_loss(self):
        print('LongOrder::stop_loss')
        self.sl_calculator.calculate()
        
    def take_profit(self):
        print('LongOrder::take_profit')
        self.tp_calculator.calculate()

    def entry_size():
        pass
    
class ShortOrder(Order):
    def stop_loss(self):
        print('ShortOrder::stop_loss')
        self.sl_calculator.calculate()

    def take_profit(self):
        print('ShortORder::take_profit')
        self.tp_calculator.calculate()

    def entry_size():
        pass


def test_long(sl_type : StopLossType, tp_type : TakeProfitType) -> None:
    order = LongOrder(sl_type, tp_type)
    order.stop_loss()
    order.take_profit()

def test_short(sl_type : StopLossType, tp_type : TakeProfitType) -> None:
    order = ShortOrder(sl_type, tp_type)
    order.stop_loss()
    order.take_profit()

if __name__ == '__main__':
    test_long(StopLossType.SLBasedOnCandleBody, TakeProfitType.RiskReward)
    test_long(StopLossType.SLPct, TakeProfitType.TPPCt)
    test_short(StopLossType.SLBasedOnCandleBody, TakeProfitType.RiskReward)
    test_short(StopLossType.SLPct, TakeProfitType.TPPCt)