
from quantfreedom.poly.sizer import Sizer, SizerType
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
    sizer = None

    def __init__(self, sl_type : StopLossType, tp_type : TakeProfitType, sizer_type : SizerType):
        self.sl_calculator = StopLossCalculator.create(sl_type)
        self.tp_calculator = TakeProfitCalculator.create(tp_type)
        self.sizer = Sizer(self.sl_calculator, sizer_type)

    def stop_loss(self):
        raise NotImplemented()
    
    def take_profit(self):
        raise NotImplemented()

    def entry_size(self):
        print('Order::entry_size')
        self.sizer.calculate()

class StopLossCalculator:
    def create(type : StopLossType):
         return SLBasedOnCandleBody() if type == StopLossType.SLBasedOnCandleBody else SLPct()
   
    def calculate(self):
        raise NotImplemented()
    
    def get_result(self):
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

    def get_result(self):
        return 'SLBasedOnCandleBody::get_result'   

class SLPct(StopLossCalculator):
    def calculate(self):
        print('SLPct')

    def get_result(self):
        return 'SLPct::get_result'

class LongOrder(Order):
    def stop_loss(self):
        print('LongOrder::stop_loss')
        self.sl_calculator.calculate()
        
    def take_profit(self):
        print('LongOrder::take_profit')
        self.tp_calculator.calculate()

    
class ShortOrder(Order):
    def stop_loss(self):
        print('ShortOrder::stop_loss')
        self.sl_calculator.calculate()

    def take_profit(self):
        print('ShortORder::take_profit')
        self.tp_calculator.calculate()


