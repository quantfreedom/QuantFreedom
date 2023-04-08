import ccxt
import pandas as pd
import numpy as np
from tqdm import tqdm
from quantfreedom._typing import Union
from re import sub


class CCXTData:
    @classmethod
    def data_download(
        cls,
        exchange: str,
        start: str,
        end: str,
        symbols: Union[str, list],
        timeframe: str,
        drop_volume: bool = True,
        remove_rate_limit: bool = False,
        bars_per_loop: int = 200,
    ):
        """
        data_download Download Data using CCXT

        Parameters
        ----------
        exchange : str
            'bybit' or 'binance' or whatever exchange works with ccxt
            http://docs.ccxt.com/#/README?id=exchanges

        start : str
            needs to be in this format '2022-01-01T00:00:00Z'

        end : str
            needs to be in this format '2022-01-01T00:00:00Z'

        symbol : list or str
            This will depend on the exchange for bybit it would be 'BTCUSDT' you will have to look this up on ccxt if you need to know.
            You can send this as a list of symbols or just one symbol.
            Here is an example of how to get the symbols list from bybit.
            ```python
            import ccxt
            exh = ccxt.bybit()
            exh.load_markets()
            exh.symbols
            ```

        timeframe : str
            '1m', '5m', '1h' '4h' '1d' '1w'

        drop_volume: bool = True
            Set this to False if you want to keep volume data.

        Returns
        -------
        Pandas dataframe
        """
        if remove_rate_limit:
            exchange = getattr(ccxt, exchange)()
        else:
            exchange = getattr(ccxt, exchange)({"enableRateLimit": True})
        print("Loading exchange data")
        exchange.load_markets()
        # exchange.verbose = True  # uncomment for debugging purposes if necessary
        start = exchange.parse8601(start)
        end = exchange.parse8601(end)
        timeframe = timeframe.lower()
        if not isinstance(symbols, list):
            symbols = [symbols]
        if not all(isinstance(x, str) for x in symbols):
            raise ValueError("your symbols must be strings")

        symbols = sorted(symbols)
        timeframe_int = int(sub(r"\D", "", timeframe))
        timeframe_str = sub(r"\d", "", timeframe)
        len_symbols = len(symbols)
        if timeframe_str == "m":
            time_in = 1000 * 60
        elif timeframe_str == "h":
            time_in = 1000 * 60 * 60
        elif timeframe_str == "d":
            time_in = 1000 * 60 * 60 * 24
        elif timeframe_str == "w":
            time_in = 1000 * 60 * 60 * 24 * 7
        elif timeframe_str == "m":
            time_in = 1000 * 60 * 60 * 24 * 7 * 12
        else:
            raise ValueError("something wrong with your timeframe")

        x = start
        timelist = [x]
        while x < end:
            x += time_in * timeframe_int
            timelist.append(x)

        final_df = pd.DataFrame(
            columns=pd.MultiIndex.from_tuples(
                tuples=[],
                name=["symbol", "candle_info"],
            ),
            index=pd.Index(
                data=pd.to_datetime(timelist, unit="ms"),
                name="open_time",
            ),
        )
        # Example if you selected your timeframe as 30 minute candles

        # Get the distance between the end date and start date in miliseconds
        # Divide that by the amount of miliseconds in what ever timeframe you set ex: there are 60,000 miliseconds in one minute.
        # Then you divide that by the number for the timeframe you set like 30 for 30 minutes to get the amount of 30 min bars in that distance of time
        # Then divide by limit because that is the amount of rows of data you can return
        # Then add one because that is the amount of loops we will have to do
        # then multiple by the amount of symbols so if we have to do 2 loops per symbol and we have 2 symbols we have to do a total of 4 loops
        # Then last we do + len of symbols because we will do an extra pbar update after we create the dataframe
        num_candles_per_coin = ((end - start) / time_in) / timeframe_int
        total_tqdm = (
            (int(num_candles_per_coin / bars_per_loop) + 1) * len_symbols
        ) + len_symbols
        print(
            f"Total possible rows of data to be download: {int(num_candles_per_coin)}\n"
            f"Total possible candles to be download: {int(num_candles_per_coin) * len_symbols}\n"
            f"It could finish earlier than expected because maybe not all coins have data starting from the start date selected."
        )
        with tqdm(total=total_tqdm) as pbar:
            # with tqdm(total=96*2) as pbar:
            for symbol in symbols:
                all_ohlcvs = []
                temp_end = end
                pbar.set_description(f"Downloading {symbol}")
                while True:
                    try:
                        ohlcvs = exchange.fetch_ohlcv(
                            symbol=symbol,
                            timeframe=timeframe,
                            since=start,
                            limit=bars_per_loop,
                            params={"end": temp_end},
                        )
                        all_ohlcvs += ohlcvs
                        if len(ohlcvs):
                            temp_end = ohlcvs[0][0] - 1
                            pbar.update(1)
                        else:
                            break

                    except Exception as e:
                        print(type(e).__name__, str(e))

                if all_ohlcvs:
                    all_ohlcvs = np.array(all_ohlcvs)
                    data_columns = pd.MultiIndex.from_tuples(
                        [
                            (symbol, "open"),
                            (symbol, "high"),
                            (symbol, "low"),
                            (symbol, "close"),
                            (symbol, "volume"),
                        ],
                        name=["symbol", "candle_info"],
                    )
                    data_index = pd.Index(
                        data=pd.to_datetime(all_ohlcvs[:, 0].flatten(), unit="ms"),
                        name="open_time",
                    )
                    data = pd.DataFrame(
                        all_ohlcvs[:, 1:],
                        columns=data_columns,
                        index=data_index,
                    )
                    if drop_volume:
                        data.drop(columns=(symbol, "volume"), inplace=True, axis=1)
                    final_df = final_df.join(data)
                pbar.update(1)
        final_df.sort_index(ascending=True, inplace=True)
        final_df.sort_index(axis=1, level=0, sort_remaining=False)
        final_df.dropna(how='all', inplace=True)
        final_df.drop(final_df.tail(1).index, inplace=True)
        return final_df
