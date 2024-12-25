import os
import requests
import sqlite3
import ta
import numpy as np
from ta import momentum, trend
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import threading
import tensorflow
from concurrent.futures import ThreadPoolExecutor, wait
from flask import Flask, jsonify, request, send_from_directory
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from keras.src.models import Sequential
from keras.src.layers import LSTM, Dense
# import matplotlib.pyplot as plt

nltk.download("vader_lexicon")
date_file_path = "last_date.txt"
write_lock = threading.Lock()
today = datetime.now().date()
conn = sqlite3.connect('stocks_history.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks_history (
        Symbol TEXT,
        Date TEXT,
        Last_Trade_Price REAL,
        Max REAL,
        Min REAL,
        Average_Price REAL,
        Change REAL,
        Volume REAL,
        Best_Turnover REAL,
        Total_Turnover REAL,
        PRIMARY KEY (Symbol, Date)
)''')
conn.commit()


def get_symbols():
    url = "https://www.mse.mk/en/stats/symbolhistory/TEL"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        dropdown = soup.find("select", {"id": "Code"})
        symbols = []

        for option in dropdown.find_all("option"):
            symbol = option.get("value")
            if not any(char.isdigit() for char in symbol): symbols.append(symbol)
        return symbols
    else:
        print("Cannot reach site.")
        return []


def get_stock_data(symbol, start_date, end_date):
    url = f"https://www.mse.mk/en/stats/symbolhistory/{symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    form_data = {"FromDate": start_date, "ToDate": end_date, "Code": symbol}
    response = requests.get(url, headers, data=form_data)
    data = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "resultsTable"})
        if table:
            for row in table.find_all("tr")[1:]:
                entry_data = row.find_all("td")

                entry = {"date": datetime.strptime(entry_data[0].text.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")}
                prices = ["last_price", "max", "min", "avg", "change", "volume", "best_turnover", "total_turnover"]
                for i, key in zip(range(1, 9), prices):
                    if entry_data[i].text.strip():
                        num_text = entry_data[i].text.replace(',', 'X')
                        num_text = num_text.replace('.', ',')
                        num_text = num_text.replace('X', '.')
                        entry[key] = num_text
                    else:
                        entry[key] = "0,00"

                data.append(entry)
                # print(f"{symbol}: {entry}")
    else:
        print("Cannot reach site.")

    return data


def store_data(issuer_code, cleaned_data):
    conn_store = sqlite3.connect('stocks_history.db')
    cursor_store = conn_store.cursor()
    columns = ["date", "last_price", "max", "min", "avg", "change", "volume", "best_turnover", "total_turnover"]

    for record in cleaned_data:
        values = [issuer_code] + [record[column] for column in columns]
        cursor_store.execute(''' 
                INSERT OR IGNORE INTO stocks_history (Symbol, Date, Last_Trade_Price, Max, Min, Average_Price, Change, Volume, Best_Turnover, Total_Turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', values)
    conn_store.commit()


def read_date_file():
    with open(date_file_path, "r") as file:
        date_string = file.read().strip()
        return datetime.strptime(date_string, "%m/%d/%Y").date()


def update_last_date():
    if not os.path.exists(date_file_path): last_date = today.replace(year=today.year-11)
    else: last_date = read_date_file()

    if (today - last_date).days < 365: last_date = today;
    else: last_date = last_date + timedelta(days=364)

    with open(date_file_path, "w") as file:
        file.write(last_date.strftime("%m/%d/%Y"))


def get_start_end_dates():
    with open(date_file_path, "r") as file:
        date_from = read_date_file()
        return date_from, date_from + timedelta(days=364)


def get_and_store_data(start_date, end_date, symbols):
    for symbol in symbols:
        raw_data = get_stock_data(symbol, start_date, end_date)
        if raw_data:
            store_data(symbol, raw_data)
        print(f"CONTINUE: {start_date} for {symbol}")


def main_pipeline():
    if not os.path.exists(date_file_path): update_last_date()
    start_date, end_date = get_start_end_dates()
    symbols = get_symbols()
    futures = []

    start_time = datetime.now()
    with ThreadPoolExecutor() as executor:
        while start_date < today:
            with write_lock:
                print(f"Starting thread for {start_date}")
                futures.append(executor.submit(get_and_store_data, start_date, end_date, symbols))
                update_last_date()
                start_date, end_date = get_start_end_dates()
                print(f"Current Start Date: {start_date}")

    wait(futures)
    print(f"Time needed to create/adjust database: {(datetime.now() - start_time).total_seconds()} seconds")


# RETRIEVE DATA
main_pipeline()
conn.close()


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


# FUNDAMENTAL ANALYSIS
def get_news_sentiment(company_name):
    urls = [
        "https://www.mse.mk/mk/news/latest/1",
        "https://www.mse.mk/mk/news/latest/2"
    ]

    news_links = []
    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch the page: {url}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        panel_body = soup.find("div", class_="panel-body")
        if panel_body:
            links = panel_body.find_all("a", href=True)
            news_links.extend([link["href"] for link in links])

    if not news_links:
        print("No news links found.")
        return

    sia = SentimentIntensityAnalyzer()
    company_sentiment = {"positive": 0, "negative": 0, "neutral": 0}
    company_news_found = False

    for link in news_links:
        if not link.startswith("http"):
            link = f"https://www.mse.mk{link}"

        response = requests.get(link)
        if response.status_code != 200:
            print(f"Failed to fetch news article: {link}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        news_text = soup.get_text()

        if company_name.lower() in news_text.lower():
            company_news_found = True
            sentiment_score = sia.polarity_scores(news_text)
            if sentiment_score["compound"] > 0.05:
                company_sentiment["positive"] += 1
            elif sentiment_score["compound"] < -0.05:
                company_sentiment["negative"] += 1
            else:
                company_sentiment["neutral"] += 1

    if not company_news_found:
        print("No information.")
        return

    positive = company_sentiment["positive"]
    negative = company_sentiment["negative"]
    neutral = company_sentiment["neutral"]

    print(f"Sentiment Analysis for {company_name}:")
    print(f"Positive news: {positive}")
    print(f"Negative news: {negative}")
    print(f"Neutral news: {neutral}")

    if positive > negative:
        print("Recommendation: Buy stocks.")
    elif negative > positive:
        print("Recommendation: Sell stocks.")
    else:
        print("Recommendation: Hold stocks.")


# PRICE PREDICTION
def create_sequences(data, target_col, sequence_length=10):
    sequences = []
    targets = []

    if isinstance(data, np.ndarray):
        raise TypeError("Expected a Pandas DataFrame, but got a NumPy array.")

    for i in range(len(data) - sequence_length):
        seq = data.iloc[i:i + sequence_length].drop(columns=[target_col]).values
        target = data.iloc[i + sequence_length][target_col]
        sequences.append(seq)
        targets.append(target)

    return np.array(sequences), np.array(targets)


def predict_prices(df):
    encoder = LabelEncoder()
    df = df.fillna(0)
    df = df.replace([np.inf, -np.inf], 0)
    df = df.drop(columns=['Symbol', 'Date', 'Max', 'Min'])
    df['RSI_signal'] = encoder.fit_transform(df['RSI_signal'])
    df['MA_signal'] = encoder.fit_transform(df['MA_signal'])
    df['Overall_signal'] = encoder.fit_transform(df['Overall_signal'])
    # scaler = MinMaxScaler()
    # df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    x, y = create_sequences(df, 'Last_Trade_Price', 10)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, shuffle=False)

    model = Sequential([
        LSTM(50, activation='relu', input_shape=(x_train.shape[1], x_train.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(x_train, y_train, epochs=10, batch_size=32, verbose=1)
    loss = model.evaluate(x_test, y_test, verbose=0)
    # print(f"Model Loss (MSE): {loss:.2f}")

    def predict_future(steps):
        future_predictions = []
        last_sequence = x_test[-1]  # Use the last test sequence as the starting point
        for _ in range(steps):
            next_prediction = model.predict(last_sequence[np.newaxis, :, :])[0, 0]
            future_predictions.append(next_prediction)
            # Ensure the new prediction matches the input feature count
            next_prediction_array = np.full((1, last_sequence.shape[1]), next_prediction)
            # Update the sequence by appending the prediction and removing the oldest value
            last_sequence = np.append(last_sequence[1:], next_prediction_array, axis=0)
        return future_predictions

    # print(df['Last_Trade_Price'])

    predictions_1_day = predict_future(1)
    last_value = (df['Last_Trade_Price'].tail(1).values[0])
    # print(last_value)
    # print(float(predictions_1_day[-1]))
    adjusted_value = round((float(predictions_1_day[-1]) + last_value)/2)

    if float(predictions_1_day[-1]) < 0 or adjusted_value > last_value * 2 or adjusted_value < last_value / 2:
        return "Not enough conclusive information to make good predictions."
    else:
        return "Future Price Prediction: " + str(adjusted_value)


# FRONTEND
app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/symbols', methods=['GET'])
def get_symbols_api():
    symbols = get_symbols()
    return jsonify(symbols)


@app.route('/company-data', methods=['GET'])
def get_company_data():
    symbol = request.args.get('symbol')
    conn = sqlite3.connect('stocks_history.db')
    cursor = conn.cursor()
    query = "SELECT * FROM stocks_history WHERE Symbol = ?"
    cursor.execute(query, (symbol,))
    rows = cursor.fetchall()
    conn.close()

    # Format data
    columns = ["Symbol", "Date", "Last_Trade_Price", "Max", "Min", "Average_Price", "Change", "Volume", "Best_Turnover",
               "Total_Turnover"]
    data = [dict(zip(columns, row)) for row in rows]
    df = aggregate_signals(generate_signals(calculate_indicators(preprocess_data(data))))
    print(df)
    print(get_news_sentiment(symbol))
    print(predict_prices(df))
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)