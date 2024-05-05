import numpy as np
from time import sleep
from requests import get
from datetime import datetime
from quantfreedom.core.enums import FootprintCandlesTuple
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange

BINANCE_USDM_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"]


class BinanceUSDM(Exchange):
    url_start = "https://fapi.binance.com"

    def __init__(self):
        pass

    def get_exchange_timeframe(
        self,
        timeframe: str,
    ):
        try:
            return BINANCE_USDM_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        except Exception as e:
            raise Exception(f"Use one of these timeframes - {UNIVERSAL_TIMEFRAMES} -> {e}")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        candles_to_dl: int = 1500,
    ) -> FootprintCandlesTuple:
        """
        Summary
        -------
        [Biance USDM candle docs](https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data)

        Explainer Video
        ---------------
        Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

        Parameters
        ----------
        symbol : str
            Use get_symbols_list if you need to know the symbols
        timeframe : str
            "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w"
        since_datetime : datetime
            The start date, in datetime format, of candles you want to download. EX: datetime(year, month, day, hour, minute)
        until_datetime : datetime
            The until date, in datetime format, of candles you want to download minus one candle so if you are on the 5 min if you say your until date is 1200 your last candle will be 1155. EX: datetime(year, month, day, hour, minute)
        candles_to_dl : int
            The amount of candles you want to download

        Returns
        -------
        np.array
            a 2 dim array with the following columns "timestamp", "open", "high", "low", "close", "volume"
        """

        end_point = "/fapi/v1/klines"
        ex_timeframe = self.get_exchange_timeframe(timeframe=timeframe)
        self.timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * self.timeframe_in_ms

        since_timestamp, until_timestamp = self.get_since_until_timestamp(
            candles_to_dl_ms=candles_to_dl_ms,
            since_datetime=since_datetime,
            timeframe_in_ms=self.timeframe_in_ms,
            until_datetime=until_datetime,
        )

        b_candles = []
        params = {
            "symbol": symbol,
            "interval": ex_timeframe,
            "startTime": since_timestamp,
            "endTime": until_timestamp,
            "limit": 1500,
        }

        while params["startTime"] + self.timeframe_in_ms < until_timestamp:
            try:
                b_data = get(url=self.url_start + end_point, params=params).json()
                last_candle_timestamp = b_data[-1][0]
                if last_candle_timestamp == params["startTime"]:
                    sleep(0.3)
                else:
                    b_candles.extend(b_data)
                    params["startTime"] = last_candle_timestamp + 2000
            except Exception as e:
                raise Exception(f"get_candles -> {e}")
        candles = np.array(b_candles, dtype=np.float_)[:, :6]
        open_timestamps = candles[:, 0].astype(np.int64)

        Footprint_Candles_Tuple = FootprintCandlesTuple(
            candle_open_datetimes=open_timestamps.astype("datetime64[ms]"),
            candle_open_timestamps=open_timestamps,
            candle_durations_seconds=np.full(candles.shape[0], int(self.timeframe_in_ms / 1000)),
            candle_open_prices=candles[:, 1],
            candle_high_prices=candles[:, 2],
            candle_low_prices=candles[:, 3],
            candle_close_prices=candles[:, 4],
            candle_asset_volumes=candles[:, 5],
            candle_usdt_volumes=np.around(a=candles[:, 5] * candles[:, 4], decimals=3),
        )
        self.last_fetched_ms_time = int(candles[-1, 0])
        return Footprint_Candles_Tuple

    def get_exchange_info(self):
        """
        [Binance Exchange Information](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information)

        Parameters
        ----------
        None

        Returns
        -------
        Dictionary
            dictionary of info about the exchange
        """
        end_point = "/fapi/v1/exchangeInfo"
        try:
            response = get(url=self.url_start + end_point).json()
            response["symbols"][0]
            return response
        except Exception as e:
            raise Exception(f"Binance get_all_symbols_info = Data or List is empty {response['message']} -> {e}")

    def get_all_symbols_info(self):
        """
        [Binance Exchange Information](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information)

        Parameters
        ----------
        None

        Returns
        -------
        Dictionary
            dictionary of info about the symbols
        """
        return self.get_exchange_info()["symbols"]

    def get_symbols_list(self):
        """
        [Binance Exchange Information](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information)

        Parameters
        ----------
        None

        Returns
        -------
        List
            List of exchange symbols
        """
        symbols = []
        for info in self.get_all_symbols_info():
            symbols.append(info["symbol"])
            symbols.sort()
        return symbols
