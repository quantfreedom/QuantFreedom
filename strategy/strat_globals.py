import json
import time

from ccxt import NotSupported


def pretty(thing):
	print(json.dumps(thing, indent=4))


def parse_timeframe(timeframe):
	amount = int(timeframe[0:-1])
	unit = timeframe[-1]
	if 'y' == unit:
		scale = 60 * 60 * 24 * 365
	elif 'M' == unit:
		scale = 60 * 60 * 24 * 30
	elif 'w' == unit:
		scale = 60 * 60 * 24 * 7
	elif 'd' == unit:
		scale = 60 * 60 * 24
	elif 'h' == unit:
		scale = 60 * 60
	elif 'm' == unit:
		scale = 60
	elif 's' == unit:
		scale = 1
	else:
		raise NotSupported('timeframe unit {} is not supported'.format(unit))
	return amount * scale


def since_time_calc(timeframe, limit):
	now = int(time.time())
	limit = limit
	duration = parse_timeframe(timeframe)
	return now - limit * duration


def get_position(exchange, symbol, side):
	if side.lower() == "buy":
		return exchange.privateGetPrivateLinearPositionList({"symbol": exchange.market(symbol)['id']})['result'][0]
	elif side.lower() == "sell":
		return exchange.privateGetPrivateLinearPositionList({"symbol": exchange.market(symbol)['id']})['result'][1]


def get_order_amount(ex, pa, s, l):
	trade_order_usd = ex.get_wallet_balance(coin="USDT")['result']['USDT']['equity'] * pa * l
	current_crypto_price = float(ex.latest_information_for_symbol(symbol=s)['result'][0]['last_price'])
	return round(trade_order_usd / current_crypto_price, 3)


def get_order_amount_binance_ccxt(ex, pa, s, l):
	trade_order_usd = float(ex.fetch_balance()['info']['assets'][3]['walletBalance']) * pa * l
	current_crypto_price = ex.fetch_tickers(symbols=[s])['BTC/USDT']['info']['lastPrice']
	return round(trade_order_usd / current_crypto_price, 3)
