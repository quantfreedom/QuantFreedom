# https://numba.discourse.group/t/typed-list-of-jitted-functions-in-jitclass/413/6


import numba
from numba.core import types


class MainClass:
    def __init__(self, num1: float, num2: types.float) -> None:
        self.num1 = num1
        self.num2 = num2


@numba.experimental.jitclass([("num1", types.float_), ("num2", types.float_)])
class SubClassOne(MainClass):
    def calc_num_one(self, number: float):
        return number * self.num1

    def calc_num_two(self, number: float):
        return number + self.num2


@numba.experimental.jitclass([("num1", types.float_), ("num2", types.float_)])
class ClassTwo(MainClass):
    def calc_num_one(self, number: float):
        return number / self.num1

    def calc_num_two(self, number: float):
        return number - self.num2


@numba.experimental.jitclass([("jitted_class", types.jitclass)])
class JitTest(object):
    def __init__(self, jitted_class):
        self.jitted_class = jitted_class

    def final_calc(self, jit_num: float):
        return self.jitted_class(number=jit_num)


do_jit_test = JitTest(ClassTwo)
do_jit_test.final_calc(jit_num=20)

