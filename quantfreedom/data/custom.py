import ccxt
import pandas as pd

class CCXTData():

    @classmethod
    def data_download(
        cls,
        exchange: str,
        start: str,
        end: str,
        symbol: str,
        timeframe: str,
    ):
        """data_download Download Data using CCXT
        
        can't do multiple coins yet
        
        Parameters
        ----------
        exchange : str
            'bybit' or 'binance' or whatever exchange works with ccxt
            http://docs.ccxt.com/#/README?id=exchanges
        start : str
            needs to be in this format '2022-01-01T00:00:00Z'
        end : str
            needs to be in this format '2022-01-01T00:00:00Z'
        symbol : str
            this will depend on the exchange for bybit it would be 'BTCUSDT' you will have to look this up on ccxt if you need to know
            this is an example of how to get the symbols list from bybit 
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
        a pandas dataframe
        """
        exchange = getattr(ccxt, exchange)()
        exchange.load_markets()
        # exchange.verbose = True  # uncomment for debugging purposes if necessary
        start = exchange.parse8601(start)
        end = exchange.parse8601(end)
        symbol = symbol
        timeframe = timeframe
        all_ohlcvs = []
        while True:
            try:
                ohlcvs = exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=start,
                    params={'end': end}
                )
                all_ohlcvs += ohlcvs
                if len(ohlcvs):
                    end = ohlcvs[0][0] - 1
                else:
                    break
            except Exception as e:
                print(type(e).__name__, str(e))
        data = pd.DataFrame(all_ohlcvs, columns=[
                            'open_time', 'open', 'high', 'low', 'close', 'volume'])
        data['open_time'] = pd.to_datetime(data['open_time'], unit='ms')
        data.set_index('open_time', inplace=True)
        data.sort_index(ascending=True, inplace=True)
        data.drop(data.tail(1).index,inplace=True)
        return data
