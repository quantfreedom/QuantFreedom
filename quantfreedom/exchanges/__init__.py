from requests import get

def get_exchange_symbols(exchange: str):
    """
    exchanges list: mufex, apex
    """
    symbols_list = []
    if exchange.lower() == "mufex":
        data_info = get(url="https://api.mufex.finance/public/v1/market/tickers").json()["data"]["list"]
    elif exchange.lower() == "apex":
        data_info = get(url="https://pro.apex.exchange/api/v1/symbols").json()["data"]["perpetualContract"]
    for _, v in enumerate(data_info):
        symbols_list.append(v["symbol"])
    return symbols_list


def get_timeframes_list():
    return ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]
