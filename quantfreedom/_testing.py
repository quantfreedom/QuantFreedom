def pivotid(
    data,
    lookback,
):  # lookback n2 before and after candle l
    pivot_list = []
    for x in range(data.shape[0]):
        if x - lookback < 0:
            pivot_list.append(0)
            continue

        pividlow = 1
        pividhigh = 1
        for i in range(x - lookback, x):
            if data.low[x] > data.low[i]:
                pividlow = 0
            if data.high[x] < data.high[i]:
                pividhigh = 0
        if pividlow and pividhigh:
            pivot_list.append(3)
        elif pividlow:
            pivot_list.append(1)
        elif pividhigh:
            pivot_list.append(2)
        else:
            pivot_list.append(3)
    data['pivot'] = pivot_list
def RSIpivotid(
    data,
    lookback,
):  # lookback n2 before and after candle l
    rsi_pivot_list = []
    for x in range(data.shape[0]):
        if x - lookback < 0:
            rsi_pivot_list.append(0)
            continue

        pividlow = 1
        pividhigh = 1
        for i in range(x - lookback, x + n2 + 1):
            if data.RSI[x] > data.RSI[i]:
                pividlow = 0
            if data.RSI[x] < data.RSI[i]:
                pividhigh = 0
        if pividlow and pividhigh:
            rsi_pivot_list.append(3)
        elif pividlow:
            rsi_pivot_list.append(1)
        elif pividhigh:
            rsi_pivot_list.append(2)
        else:
            rsi_pivot_list.append(3)
    data['RSIpivot'] = rsi_pivot_list
pivotid(df, 5, 5)
RSIpivotid(df, 5, 5)
df.head()