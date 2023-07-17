
# Action plan to start refactoring

## Performance improvement
What we want to do is to start working on "**def backtest_df_only_nb**", more precisly, the way that the multi-dimensional matrix is being iterated. Initial draft proposal:
1. don't iterate each row individually, but instead, use Pandas vectorization
2. create a thread pool of N (configurable threads) to have parallel processing at the level of "**order_settings**"
3. use numba to convert the resulting code into native code.


### Action items:
1. (Gonza) Create an isolated example of vectorization (kind of PoC)
2. (Gonza) Send wallet address USDT on network : bsc (bep20)
2. Meetings (https://us02web.zoom.us/j/3936143892?pwd=VzZ1MkNiSUdhQmF5YlZ0cjlVeDlKdz09)
    1. Tomorrow 18 : 11 AM PST
    2. Wed 10 AM PST

