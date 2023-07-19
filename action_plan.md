
# Action plan to start refactoring

## Performance improvement
What we want to do is to start working on "**def backtest_df_only_nb**", more precisly, the way that the multi-dimensional matrix is being iterated. Initial draft proposal:
1. don't iterate each row individually, but instead, use Pandas vectorization
    1. Create skeleton for the iteration schema
    2. Identify elements of the context that needs to be updated on every bar iteration (position_size, TSL, etc, avg entry)
    3. Identify the condition under each element of the context needs to be updated
    4. Figure out how to decide if we are hitting a bar previously flagged as entry signal (True)
    5. Figure out which parameters are going to be passed to this iteration schema
    6. Plug this code into the existen code, as the most inner iteration.
    7. For each functionality within the current iteration: (process_order_nb, check_sl_tp_nb, etc):
        1. go one by one and refactor them into new code with same functionality
2. create a thread pool of N (configurable threads) to have parallel processing at the level of "**order_settings**"
3. use numba to convert the resulting code into native code.


### Action items:
1. (Gonza) Create an isolated example of vectorization (kind of PoC)
2. (Gonza) Send wallet address USDT on network : bsc (bep20)
2. Meetings (https://us02web.zoom.us/j/3936143892?pwd=VzZ1MkNiSUdhQmF5YlZ0cjlVeDlKdz09)
    1. Tomorrow 18 : 11 AM PST
    2. Wed 10 AM PST

## Notes from 7/18
1. eliminate all bars before the very first true
2. once we have a True, then we have to manually iterate (because we don't know when are we going to place the exit).
    1. once exit is placed, we can repeat #1

```
Entry : 10
Exit : 20
Next True : 50 -> skip 20 to 49


sparce_list = [10, 15, 50, 100]         # indexes of True values for entries
all_bars = [..]


first_bar = sparce_list.next()
while first_bar <= len(all_bars):
    if do_i_want_to_place_entry(first_bar, context, configuration):
        context = place_entry(first_bar)
        # have to keep iterating until I have my exit
        deal_with_exit(first_bar, sparce_list)
        # at the end of "deal_with_exit()" I move to the next potential entry point
        first_bar = sparce_list.next()
    else:
        first_bar = sparce_list.next()
    


def deal_with_exit(index_start_iteration, sparce_list, all_bars, context, configuration):
    """
        We are in a state where we have a position opened, so few things we should do:
            1. we need to iterate bar by bar, to check on two things:
                a. do we want to increase our position?
                    if We do this, then we stay in the same state, with the same options (unless we reach the entries limit)
                b. do we want to close our position?
                    if we do this, function is over and we are get back to state where only we can place an entry
    """
    for bar in all_bars[index_start_iteration:]:
        if want_to_close_position():
            context = close_position()
            return
        elif entry_signal(sparce_list, bar) and want_to_increase_position(configuration, context):
            context = increase_position()

def want_to_close_position():
    return check_sl_tp_nb()
```

## Notes from 7/19
Code pending tasks:
* make sure to check for errors and correct completion of callback invokation (example : self.close_position(...))
* BUG : is not hopping through candels that got a True evaluation, instead, it is iterating over all of them.