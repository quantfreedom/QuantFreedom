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
