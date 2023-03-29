import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objs as go
import talib
import ccxt

# Initialize Bybit client
exchange = ccxt.bybit()

# Load Bitcoin data
symbol = 'BTC/USDT'
timeframe = '4h'
since = exchange.parse8601('2023-01-01T00:00:00Z')
klines = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since)
df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

# Convert timestamp to datetime and set as index
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Calculate the 300 EMA
ema = talib.EMA(df['Close'], timeperiod=50)

# Calculate the RSI and the 20-day EMA of RSI
rsi = talib.RSI(df['Close'], timeperiod=20)
rsi_ema = talib.EMA(rsi, timeperiod=20)

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(style={'backgroundColor': 'rgb(17, 17, 17)'}, children=[
    html.H1(style={'textAlign': 'center', 'color': '#ffffff'}, children='Bitcoin Data'),

    dcc.Graph(
        id='btc-graph',
        figure={
            'data': [
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    increasing=dict(line=dict(color='#00ff00')),
                    decreasing=dict(line=dict(color='#ff0000'))
                ),
                go.Scatter(
                    x=df.index,
                    y=ema,
                    line=dict(color='#ffff00', width=2),
                    name='300 EMA'
                ),
            ],
            'layout': go.Layout(
                title=f'{symbol} {timeframe} Candles',
                xaxis=dict(title='Time'),
                yaxis=dict(title='Price (USDT)'),
                template='plotly_dark'
            )
        }
    ),

    dcc.Graph(
        id='rsi-graph',
        figure={
            'data': [
                go.Scatter(
                    x=df.index,
                    y=rsi,
                    line=dict(color='#ffffff', width=2),
                    name='RSI'
                ),
                go.Scatter(
                    x=df.index,
                    y=rsi_ema,
                    line=dict(color='#ffff00', width=2),
                    name='20 EMA'
                ),
            ],
            'layout': go.Layout(
                title=f'{symbol} RSI (20 day window)',
                xaxis=dict(title='Time'),
                yaxis=dict(title='RSI'),
                template='plotly_dark'
            )
        }
    )
], className='dash-bootstrap')

if __name__ == '__main__':
    app.run_server(debug=True)
