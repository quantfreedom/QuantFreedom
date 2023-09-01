

from enum import Enum

class StopLossType(Enum):
    SLBasedOnCandleBody = 1
    SLPct = 2

class Order:
    sl_calculator = None

    def __init__(self, sl_type : StopLossType):
        self.sl_calculator = StopLossCalculator.create(sl_type)

    def stop_loss():
        raise NotImplemented()

    def entry_size():
        raise NotImplemented()



class StopLossCalculator:
    def calculate(self):
        raise NotImplemented()

    def create(type : StopLossType):
         return SLBasedOnCandleBody() if type == StopLossType.SLBasedOnCandleBody else SLPct()

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

    def entry_size():
        pass


class ShortOrder(Order):
    def stop_loss(self):
        print('ShortOrder::stop_loss')
        self.sl_calculator.calculate()

    def entry_size():
        pass


def test_long(sl_type : StopLossType) -> None:
    order = LongOrder(sl_type)
    order.stop_loss()

def test_short(sl_type : StopLossType) -> None:
    order = ShortOrder(sl_type)
    order.stop_loss()


if __name__ == '__main__':
    test_long(StopLossType.SLBasedOnCandleBody)
    test_long(StopLossType.SLPct)
    test_short(StopLossType.SLBasedOnCandleBody)
    test_short(StopLossType.SLPct)