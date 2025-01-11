import ta
from ta import momentum, trend
import pandas as pd


def preprocess_data(data):
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    for col in ['Last_Trade_Price', 'Max', 'Min', 'Average_Price', 'Change', 'Best_Turnover', 'Total_Turnover']:
        df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df.sort_values(by='Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# TECHNICAL ANALYSIS FUNCTIONS
def calculate_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Last_Trade_Price']).rsi()
    df['Stochastic'] = ta.momentum.StochasticOscillator(high=df['Max'], low=df['Min'], close=df['Last_Trade_Price']).stoch()
    df['MACD'] = ta.trend.MACD(close=df['Last_Trade_Price']).macd()
    df['Momentum'] = df['Last_Trade_Price'].diff()
    df['CCI'] = ta.trend.CCIIndicator(high=df['Max'], low=df['Min'], close=df['Last_Trade_Price']).cci()
    df['SMA'] = ta.trend.SMAIndicator(close=df['Last_Trade_Price'], window=14).sma_indicator()
    df['EMA'] = ta.trend.EMAIndicator(close=df['Last_Trade_Price'], window=14).ema_indicator()
    df['WMA'] = df['Last_Trade_Price'].rolling(window=14).apply(lambda x: (x * range(1, len(x)+1)).sum() / sum(range(1, len(x)+1)))
    df['MAE_upper'], df['MAE_lower'] = df['SMA'] * 1.02, df['SMA'] * 0.98
    df['HMA'] = ta.trend.WMAIndicator(close=df['Last_Trade_Price'], window=14).wma()

    return df


def generate_signals(df):
    df['RSI_signal'] = df['RSI'].apply(lambda x: 'Buy' if x < 30 else 'Sell' if x > 70 else 'Hold')
    df['MA_signal'] = df.apply(lambda row: 'Buy' if row['SMA'] < row['EMA'] else 'Sell' if row['SMA'] > row['EMA'] else 'Hold', axis=1)
    # Dovrshi
    return df


def aggregate_signals(df):
    signals = ['RSI_signal', 'MA_signal']
    df['Overall_signal'] = df[signals].mode(axis=1)[0]
    return df


def get_signal_dataframe(data):
    return generate_signals(calculate_indicators(preprocess_data(data)))
