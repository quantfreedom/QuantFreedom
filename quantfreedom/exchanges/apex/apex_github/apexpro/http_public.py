from apexpro import HTTP
from apexpro.constants import URL_SUFFIX


class HttpPublic(HTTP):
    def server_time(self, **kwargs):
        """"
        GET Retrieve System Time.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#publicapi-get-apex-server-time
        :returns: Request results as dictionary.
        """

        suffix = URL_SUFFIX + "/v1/time"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix
        )

    def depth(self, **kwargs):
        """"
        GET Retrieve Market Depth.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#publicapi-get-retrieve-market-depth
        :returns: Request results as dictionary.
        """
        suffix = URL_SUFFIX + "/v1/depth"
        if kwargs['symbol'] is not None:
            kwargs['symbol'] = kwargs['symbol'].replace('-', '')
        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def trades(self, **kwargs):
        """"
        GET Retrieve Newest Trading Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#publicapi-get-retrieve-newest-trading-data
        :returns: Request results as dictionary.
        """
        suffix = URL_SUFFIX + "/v1/trades"
        if kwargs['symbol'] is not None:
            kwargs['symbol'] = kwargs['symbol'].replace('-', '')
        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def klines(self, **kwargs):
        """"
        GET Retrieve Candlestick Chart Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#publicapi-get-retrieve-candlestick-chart-data
        :returns: Request results as dictionary.
        """
        suffix = URL_SUFFIX + "/v1/klines"
        if kwargs['symbol'] is not None:
            kwargs['symbol'] = kwargs['symbol'].replace('-', '')
        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def ticker(self, **kwargs):
        """"
        GET Retrieve Ticker Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#publicapi-get-retrieve-ticker-data
        :returns: Request results as dictionary.
        """
        suffix = URL_SUFFIX + "/v1/ticker"
        if kwargs['symbol'] is not None:
            kwargs['symbol'] = kwargs['symbol'].replace('-', '')
        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def history_funding(self, **kwargs):
        """"
        GET Retrieve Funding Rate History.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#publicapi-get-retrieve-funding-rate-history
        :returns: Request results as dictionary.
        """
        suffix = URL_SUFFIX + "/v1/history-funding"
        #if kwargs['symbol'] is not None:
        #    kwargs['symbol'] = kwargs['symbol'].replace('-', '')
        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )
