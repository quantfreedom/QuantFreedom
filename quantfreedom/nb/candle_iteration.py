import logging
import pandas as pd
import requests
import random

class CandleIteration:
    """
        TODO:

    """
    candles = None
    entry_signals = None 
    user_configuration = None
    context = None                      # FIXME : define more clearly what context actually is? SL value? TP value? positions opened? avg position value? user configuration?
    current_positions = None

    # callbacks
    evaluate_entry_signal = None        # signature : (candle, context, configuration) -> bool
    evaluate_increase_position = None   # signature : (candle, context, configuration, current_positions) -> bool
    evaluate_stop_loss = None            # signature : (candle, context, configuration, current_positions) -> bool
    evaluate_take_profit = None         # signature : (candle, context, configuration, current_positions) -> bool
    place_entry = None                  # signature : (candle, context, configuration) -> candle
    close_position = None               # signature : (candle, context, configuration, current_positions) -> bool
    adjust_st_trailing = None           # signature : (candle, context, configuration) -> None

    def __init__(self, user_configuration, candles, entry_signals, evaluate_entry_signal, evaluate_increase_position, evaluate_stop_loss, evaluate_take_profit, place_entry, close_position, adjust_stop_loss_trailing):
        """
            candles : OCHL
        """
        self.candles = candles
        self.entry_signals = entry_signals
        self.user_configuration = user_configuration
        self.context = {'SP_TRAILING':0, 'TP':0, 'POSITIONS':[]}
        self.current_positions = []


        self.evaluate_entry_signal = evaluate_entry_signal
        self.evaluate_increase_position = evaluate_increase_position
        self.evaluate_stop_loss = evaluate_stop_loss
        self.evaluate_take_profit = evaluate_take_profit
        self.place_entry = place_entry
        self.close_position = close_position
        self.adjust_st_trailing = adjust_stop_loss_trailing

        # TODO : any other parameter?

    def iterate(self):
        next_entry_signal_df = self.candles[self.entry_signals]

        while next_entry_signal_df.empty == False:
            current_candle = next_entry_signal_df.iloc[0]
            if self.evaluate_entry_signal(current_candle, self.context, self.user_configuration):
                # entering into ENTRY_PLACED stated
                self.current_positions.append(self.place_entry(current_candle, self.context, self.user_configuration))

                # during ENTRY_PLACED state, we can:
                # 1. increase our position
                # 2. step out our position (after hitting SL)
                # 3. take profit (after hitting TP)
                # 4. update stop loss trailing

                last_iterated_candle_index = self.__individual_iteration(self.__get_index_from_candle(current_candle)+1)
                next_entry_signal_df = self.__get_next_entry_signal(last_iterated_candle_index)
            else:
                next_entry_signal_df = self.__get_next_entry_signal(self.__get_index_from_candle(current_candle))

    
    #------- AUX METHODS ------
    def __get_index_from_candle(self, candle):
        return candle.name
    
    def __get_next_entry_signal(self, current_entry):
        return self.candles[current_entry+1:][self.entry_signals[current_entry+1:]]

    def __individual_iteration(self, starting_index):
        current_index = starting_index
        iterating_df = self.candles[starting_index:]
        for index, candle in iterating_df.iterrows():
            if self.entry_signals[current_index] and \
                    self.evaluate_increase_position(candle, self.context, self.user_configuration, self.current_positions):
                self.current_positions.append(self.place_entry(self.context, self.user_configuration))          # TODO : can I use the same callback or do I need a different one because it is an increase instead of a first-time entry?
            elif self.evaluate_stop_loss(candle, self.context, self.user_configuration, self.current_positions):
                self.__close_position(candle, 'stop_loss')
                self.current_positions = []
                break                   # since we close position, we can get back to jumping candles between true signals
            elif self.evaluate_take_profit(candle, self.context, self.user_configuration, self.current_positions):
                self.__close_position(candle, 'take_profit')
                self.current_positions = []
                break                   # since we close position, we can get back to jumping candles between true signals

            if self.__is_any_open_position():
                self.adjust_st_trailing(candle, self.context, self.user_configuration)
            
            current_index += 1

        return current_index

    def __is_any_open_position(self):
        return len(self.context.setdefault('POSITIONS', []))

    def __close_position(self, candle, reason):
        self.close_position(candle, self.context, self.user_configuration, self.current_positions)
        self.__clear_tracking_values()

    def __clear_tracking_values(self):
        self.context['SP_TRAILING'] = 0
        self.context['TP'] = 0
        self.context['POSITIONS'] = []


######################### TESTING FUNCTIONS #########################
def download_btc_candles(interval='1h', limit=1000):
    """
    Download BTC candlestick data from Binance.

    Parameters:
        interval (str): The interval for the candlesticks. Options: '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h',
                        '6h', '8h', '12h', '1d', '3d', '1w', '1M'.
        limit (int): The number of candlesticks to retrieve. Maximum is 1000.

    Returns:
        pandas.DataFrame: A DataFrame containing the candlestick data.
    """
    base_url = 'https://api.binance.com/api/v1/klines'
    params = {
        'symbol': 'BTCUSDT',
        'interval': interval,
        'limit': limit
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                     'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                     'taker_buy_quote_asset_volume', 'ignore'])

    df = df.astype(dtype={'timestamp':str, 'open':float, 'high':float, 'low':float, 'close':float, 'volume':float, 'close_time':float, 'quote_asset_volume':float, 'number_of_trades':float, 'taker_buy_base_asset_volume':float, 'taker_buy_quote_asset_volume':float, 'ignore':float})

    # Convert timestamp to a human-readable date
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_entry_signals(candles):
    return candles.close < 28000


def evaluate_entry_signal(candle, context, configuration):
    logging.info(f'[EVALUATING_ENTRY_SIGNAL] [timestamp={str(candle.timestamp)}] [close={candle.close}]')
    return random.randint(1,20) > 10            #50% chances of getting in

def evaluate_increase_position(candle, context, configuration, current_positions):
    logging.info(f'[EVALUATING_INCREASE_POSITION] [timestamp={str(candle.timestamp)}] [close={candle.close}]')
    return False

def evaluate_stop_loss(candle, context, configuration, current_positions):
    logging.info(f'[EVALUATING_STOP_LOSS] [timestamp={str(candle.timestamp)}] [close={candle.close}]')
    return random.randint(1,20) > 16             #20% chances of getting out by stop_loss

def evaluate_take_profit(candle, context, configuration, current_positions):
    logging.info(f'[EVALUATING_TAKE_PROFIT] [timestamp={str(candle.timestamp)}] [close={candle.close}]')
    return random.randint(1,20) > 18             #10% chances of getting out by taking profit

def place_entry(candle, context, configuration):
    logging.info(f'[PLACING_ENTRY] [timestamp={str(candle.timestamp)}] [close={candle.close}]')
    return candle

def close_position(candle, context, configuration, current_positions):
    logging.info(f'[CLOSING_POSITION] [timestamp={str(candle.timestamp)}] [close={candle.close}]')
    return False
    
def adjust_stop_loss_trailing(candle, context, configuration):
    logging.info(f'[UPDATING_STOP_LOSS_TRAILING] [timestamp={str(candle.timestamp)}] [close={candle.close}]')


def run_test():
    interval = '1h'
    limit = 10000
    candles = download_btc_candles(interval=interval, limit=limit)
    entry_signals = calculate_entry_signals(candles)
    iter = CandleIteration(user_configuration={},
                            candles=candles,
                            entry_signals=entry_signals,
                            evaluate_entry_signal=evaluate_entry_signal,
                            evaluate_increase_position=evaluate_increase_position,
                            evaluate_stop_loss=evaluate_stop_loss,
                            evaluate_take_profit=evaluate_take_profit,
                            place_entry=place_entry,
                            close_position=close_position,
                            adjust_stop_loss_trailing=adjust_stop_loss_trailing)
    
    iter.iterate()

def configure_logging():
    root = logging.getLogger()

    try:
        handler = logging.FileHandler(filename='output.log', mode='w')
    except Exception as e:
        print(f'Couldnt init logging system with file [output.log]. Desc=[{e}]')
        return False

    print(f'Configuring log level [INFO]')
    root.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

if __name__ == '__main__':
    configure_logging()
    run_test()