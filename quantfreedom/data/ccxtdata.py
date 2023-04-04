import ccxt
import pandas as pd
import numpy as np
from quantfreedom._typing import Union


class CCXTData:
    @classmethod
    def data_download(
        cls,
        exchange: str,
        start: str,
        end: str,
        symbols: Union[str, list],
        timeframe: str,
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

        Returns
        -------
        Pandas dataframe
        """
        exchange = getattr(ccxt, exchange)()
        exchange.load_markets()
        # exchange.verbose = True  # uncomment for debugging purposes if necessary
        start = exchange.parse8601(start)
        end = exchange.parse8601(end)
        timeframe = timeframe
        final_df = pd.DataFrame()

        if not isinstance(symbols, list):
            symbols = [symbols]
        if not all(isinstance(x, str) for x in symbols):
            raise ValueError("your symbols must be strings")

        for symbol in symbols:
            all_ohlcvs = []
            temp_end = end
            while True:
                try:
                    ohlcvs = exchange.fetch_ohlcv(
                        symbol=symbol,
                        timeframe=timeframe,
                        since=start,
                        params={"end": temp_end},
                    )
                    all_ohlcvs += ohlcvs
                    if len(ohlcvs):
                        temp_end = ohlcvs[0][0] - 1
                    else:
                        break
                except Exception as e:
                    print(type(e).__name__, str(e))
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
            data.sort_index(ascending=True, inplace=True)
            data.drop(data.tail(1).index, inplace=True)
            final_df = data.join(final_df)
        return final_df
