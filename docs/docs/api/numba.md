---
title: Numba Functions
---
Provides an arsenal of Numba-compiled functions
modeling, such as generating and filling orders. These only accept NumPy arrays and
other Numba-compatible types.
!!! warning
    Accumulation of roundoff error possible.
    See [here](https://en.wikipedia.org/wiki/Round-off_error#Accumulation_of_roundoff_error) for explanation.
    Rounding errors can cause trades and positions to not close properly:
    ```pycon
    >>> print('%.50f' % 0.1)  # has positive error
    0.10000000000000000555111512312578270211815834045410
    >>> # many buy transactions with positive error -> cannot close position
    >>> sum([0.1 for _ in range(1000000)]) - 100000
    1.3328826753422618e-06
    >>> print('%.50f' % 0.3)  # has negative error
    0.29999999999999998889776975374843459576368331909180
    >>> # many sell transactions with negative error -> cannot close position
    >>> 300000 - sum([0.3 for _ in range(1000000)])
    5.657668225467205e-06
    ```
    
::: quantfreedom.nb.buy_funcs
::: quantfreedom.nb.execute_funcs
::: quantfreedom.nb.helper_funcs
::: quantfreedom.nb.sell_funcs